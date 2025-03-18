from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from products.models import Product
import stripe
import json
from django.http import JsonResponse
from cart.models import Cart, CartItem

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Cart functionality
# We'll use session-based cart for simplicity
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart(request):
    cart_items = request.session.get('cart', {})
    
    if not cart_items:
        return Response({'items': [], 'total': 0})
    
    items = []
    total = 0
    
    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = product.price * quantity
            total += item_total
            
            items.append({
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'image': product.image.url if product.image else None
                },
                'quantity': quantity,
                'total': float(item_total)
            })
        except Product.DoesNotExist:
            # Remove invalid product from cart
            cart_items.pop(product_id, None)
            request.session['cart'] = cart_items
            request.session.modified = True
    
    return Response({
        'items': items,
        'total': float(total)
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.data.get('quantity', 1))
    
    if quantity <= 0:
        return Response({'error': 'Quantity must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
    
    if product.stock < quantity:
        return Response({'error': 'Not enough stock available'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get or initialize cart
    cart_items = request.session.get('cart', {})
    
    # Convert product_id to string since session keys must be strings
    product_id_str = str(product_id)
    
    # Add or update product in cart
    if product_id_str in cart_items:
        cart_items[product_id_str] += quantity
    else:
        cart_items[product_id_str] = quantity
    
    # Save cart to session
    request.session['cart'] = cart_items
    request.session.modified = True
    
    return Response({'message': 'Product added to cart'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, product_id):
    # Get cart
    cart_items = request.session.get('cart', {})
    
    # Convert product_id to string
    product_id_str = str(product_id)
    
    # Remove product from cart
    if product_id_str in cart_items:
        del cart_items[product_id_str]
        
        # Save cart to session
        request.session['cart'] = cart_items
        request.session.modified = True
        
        return Response({'message': 'Product removed from cart'})
    
    return Response({'error': 'Product not in cart'}, status=status.HTTP_400_BAD_REQUEST)

# Order functionality
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    # For customers, show their orders
    if request.user.user_type == 'customer':
        orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    # For store owners, show orders containing their products
    elif request.user.user_type == 'store_owner' and hasattr(request.user, 'store'):
        store = request.user.store
        order_items = OrderItem.objects.filter(product__store=store)
        orders = Order.objects.filter(items__in=order_items).distinct().order_by('-created_at')
    else:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    try:
        # For customers, check if the order belongs to them
        if request.user.user_type == 'customer':
            order = Order.objects.get(id=order_id, customer=request.user)
        # For store owners, check if the order contains their products
        elif request.user.user_type == 'store_owner' and hasattr(request.user, 'store'):
            store = request.user.store
            order_items = OrderItem.objects.filter(product__store=store, order_id=order_id)
            if not order_items.exists():
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
            order = Order.objects.get(id=order_id)
        else:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderSerializer(order)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    # Check if user is a customer
    if request.user.user_type != 'customer':
        return Response({'error': 'Only customers can create orders'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get cart
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not cart_items:
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate shipping address
    if not request.data.get('shipping_address'):
        return Response({'error': 'Shipping address is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate total amount
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    
    # Create order
    import uuid
    order_number = str(uuid.uuid4()).split('-')[0].upper()
    
    order = Order.objects.create(
        customer=request.user,
        order_number=order_number,
        total_amount=total_amount,
        shipping_address=request.data.get('shipping_address'),
    )
    
    # Create order items
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
        
        # Update product stock
        product = item.product
        product.stock -= item.quantity
        product.save()
    
    # Clear cart
    cart_items.delete()
    
    return Response({
        'message': 'Order created successfully',
        'order': OrderSerializer(order).data
    }, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    # Check if user is a store owner
    if request.user.user_type != 'store_owner' or not hasattr(request.user, 'store'):
        return Response({'error': 'Only store owners can update order status'}, 
                        status=status.HTTP_403_FORBIDDEN)
    
    store = request.user.store
    
    try:
        # Check if order contains products from this store
        order_items = OrderItem.objects.filter(product__store=store, order_id=order_id)
        if not order_items.exists():
            return Response({'error': 'Order not found or does not contain your products'}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Update status
    new_status = request.data.get('status')
    if new_status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    
    order.status = new_status
    order.save()
    
    serializer = OrderSerializer(order)
    return Response({
        'message': 'Order status updated successfully',
        'order': serializer.data
    })

# Checkout and payment
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkout(request):
    # Get cart items
    cart_items = request.session.get('cart', {})
    
    if not cart_items:
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
    items = []
    total = 0
    
    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = product.price * quantity
            total += item_total
            
            items.append({
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'image': product.image.url if product.image else None
                },
                'quantity': quantity,
                'total': float(item_total)
            })
        except Product.DoesNotExist:
            # Remove invalid product from cart
            cart_items.pop(product_id, None)
            request.session['cart'] = cart_items
            request.session.modified = True
    
    return Response({
        'items': items,
        'total': float(total)
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payment(request):
    # Get cart items
    cart_items = request.session.get('cart', {})
    
    if not cart_items:
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate total amount
    total = 0
    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            total += product.price * quantity
        except Product.DoesNotExist:
            # Remove invalid product from cart
            cart_items.pop(product_id, None)
            request.session['cart'] = cart_items
            request.session.modified = True
    
    # Create Stripe checkout session
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Order Payment',
                        },
                        'unit_amount': int(total * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url=request.build_absolute_uri('/api/orders/payment/success/'),
            cancel_url=request.build_absolute_uri('/api/orders/payment/cancel/'),
        )
        
        # Store checkout session ID in session
        request.session['checkout_session_id'] = checkout_session.id
        request.session.modified = True
        
        return Response({'checkout_url': checkout_session.url})
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_success(request):
    # Get checkout session ID
    checkout_session_id = request.session.get('checkout_session_id')
    
    if not checkout_session_id:
        return Response({'error': 'No payment session found'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Retrieve checkout session
        checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)
        
        # Create order
        cart_items = request.session.get('cart', {})
        
        if not cart_items:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Convert cart items to order items format
        items = []
        for product_id, quantity in cart_items.items():
            items.append({
                'product_id': int(product_id),
                'quantity': quantity
            })
        
        # Create order data
        order_data = {
            'shipping_address': request.data.get('shipping_address', ''),
            'items': items
        }
        
        serializer = OrderCreateSerializer(data=order_data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            
            # Update order with payment information
            order.payment_status = True
            order.stripe_payment_id = checkout_session.payment_intent
            order.save()
            
            # Clear cart and checkout session
            request.session['cart'] = {}
            request.session.pop('checkout_session_id', None)
            request.session.modified = True
            
            return Response({
                'message': 'Payment successful and order created',
                'order': OrderSerializer(order).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_cancel(request):
    # Clear checkout session
    request.session.pop('checkout_session_id', None)
    request.session.modified = True
    
    return Response({'message': 'Payment cancelled'})

# Frontend Views
@login_required
def checkout_page(request):
    # Check if user is a customer
    if request.user.user_type != 'customer':
        messages.error(request, 'Only customers can checkout.')
        return redirect('home')
    
    # Get cart
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')
    
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')
    
    # Calculate total amount
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        # Create order
        import uuid
        order_number = str(uuid.uuid4()).split('-')[0].upper()
        
        shipping_address = request.POST.get('shipping_address')
        
        if not shipping_address:
            messages.error(request, 'Shipping address is required.')
            return render(request, 'orders/checkout.html', {'cart_items': cart_items, 'total_amount': total_amount})
        
        order = Order.objects.create(
            customer=request.user,
            order_number=order_number,
            total_amount=total_amount,
            shipping_address=shipping_address,
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            
            # Update product stock
            product = item.product
            product.stock -= item.quantity
            product.save()
        
        # Clear cart
        cart_items.delete()
        
        messages.success(request, 'Order created successfully.')
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'orders/checkout.html', {'cart_items': cart_items, 'total_amount': total_amount})

@login_required
def order_list_page(request):
    # For customers, show their orders
    if request.user.user_type == 'customer':
        orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    # For store owners, show orders containing their products
    elif request.user.user_type == 'store_owner' and hasattr(request.user, 'store'):
        store = request.user.store
        order_items = OrderItem.objects.filter(product__store=store)
        orders = Order.objects.filter(items__in=order_items).distinct().order_by('-created_at')
    else:
        messages.error(request, 'Unauthorized')
        return redirect('home')
    
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail_page(request, order_id):
    try:
        # For customers, check if the order belongs to them
        if request.user.user_type == 'customer':
            order = Order.objects.get(id=order_id, customer=request.user)
        # For store owners, check if the order contains their products
        elif request.user.user_type == 'store_owner' and hasattr(request.user, 'store'):
            store = request.user.store
            order_items = OrderItem.objects.filter(product__store=store, order_id=order_id)
            if not order_items.exists():
                messages.error(request, 'Order not found')
                return redirect('order_list')
            order = Order.objects.get(id=order_id)
        else:
            messages.error(request, 'Unauthorized')
            return redirect('home')
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('order_list')
    
    # Get order items
    order_items = OrderItem.objects.filter(order=order)
    
    # For store owners, only show their products
    if request.user.user_type == 'store_owner' and hasattr(request.user, 'store'):
        store = request.user.store
        order_items = order_items.filter(product__store=store)
    
    context = {
        'order': order,
        'order_items': order_items
    }
    
    return render(request, 'orders/order_detail.html', context)

@login_required
def create_order_view(request):
    # Check if user is a customer
    if request.user.user_type != 'customer':
        messages.error(request, 'Only customers can create orders.')
        return redirect('home')
    
    # Get cart
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')
    
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')
    
    # Calculate total amount
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        # Create order
        import uuid
        order_number = str(uuid.uuid4()).split('-')[0].upper()
        
        shipping_address = request.POST.get('shipping_address')
        
        if not shipping_address:
            messages.error(request, 'Shipping address is required.')
            return render(request, 'orders/checkout.html', {'cart_items': cart_items, 'total_amount': total_amount})
        
        order = Order.objects.create(
            customer=request.user,
            order_number=order_number,
            total_amount=total_amount,
            shipping_address=shipping_address,
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            
            # Update product stock
            product = item.product
            product.stock -= item.quantity
            product.save()
        
        # Clear cart
        cart_items.delete()
        
        messages.success(request, 'Order created successfully.')
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'orders/checkout.html', {'cart_items': cart_items, 'total_amount': total_amount})

@login_required
def update_order_status_view(request, order_id):
    if request.method == 'POST':
        # Check if user is a store owner
        if request.user.user_type != 'store_owner' or not hasattr(request.user, 'store'):
            messages.error(request, 'Only store owners can update order status')
            return redirect('home')
        
        store = request.user.store
        
        try:
            # Check if order contains products from this store
            order_items = OrderItem.objects.filter(product__store=store, order_id=order_id)
            if not order_items.exists():
                messages.error(request, 'Order not found or does not contain your products')
                return redirect('order_list')
            
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found')
            return redirect('order_list')
        
        # Update status
        new_status = request.POST.get('status')
        if new_status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
            messages.error(request, 'Invalid status')
            return redirect('order_detail', order_id=order.id)
        
        order.status = new_status
        order.save()
        
        messages.success(request, 'Order status updated successfully')
        return redirect('order_detail', order_id=order.id)
    
    return redirect('order_detail', order_id=order_id)
