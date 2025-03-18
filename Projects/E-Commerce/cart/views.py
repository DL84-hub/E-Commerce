from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product

# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_detail(request):
    # Get or create cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get cart items
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Calculate total
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    # Serialize cart
    serializer = CartSerializer(cart)
    
    return Response({
        'cart': serializer.data,
        'total': total
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    # Get product
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))
    
    if not product_id:
        return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if quantity is valid
    if quantity <= 0:
        return Response({'error': 'Quantity must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if product is in stock
    if product.stock < quantity:
        return Response({'error': f'Not enough stock. Available: {product.stock}'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if product is already in cart
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        # Update quantity
        cart_item.quantity += quantity
        cart_item.save()
    except CartItem.DoesNotExist:
        # Create new cart item
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
    
    # Serialize cart
    serializer = CartSerializer(cart)
    
    return Response({
        'message': 'Product added to cart',
        'cart': serializer.data
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    # Get cart item
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
    except CartItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get quantity
    quantity = int(request.data.get('quantity', 1))
    
    # Check if quantity is valid
    if quantity <= 0:
        return Response({'error': 'Quantity must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if product is in stock
    if cart_item.product.stock < quantity:
        return Response({'error': f'Not enough stock. Available: {cart_item.product.stock}'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update quantity
    cart_item.quantity = quantity
    cart_item.save()
    
    # Serialize cart
    serializer = CartSerializer(cart_item.cart)
    
    return Response({
        'message': 'Cart item updated',
        'cart': serializer.data
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    # Get cart item
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
    except CartItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Delete cart item
    cart_item.delete()
    
    # Serialize cart
    serializer = CartSerializer(cart_item.cart)
    
    return Response({
        'message': 'Product removed from cart',
        'cart': serializer.data
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    # Get cart
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Delete all cart items
    CartItem.objects.filter(cart=cart).delete()
    
    # Serialize cart
    serializer = CartSerializer(cart)
    
    return Response({
        'message': 'Cart cleared',
        'cart': serializer.data
    })

# Frontend Views
@login_required
def cart_page(request):
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get cart items
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Calculate total
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    
    return render(request, 'cart/cart.html', context)

@login_required
def add_to_cart_view(request, product_id):
    if request.method == 'POST':
        # Get product
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Get quantity
        quantity = int(request.POST.get('quantity', 1))
        
        # Check if quantity is valid
        if quantity <= 0:
            messages.error(request, 'Quantity must be greater than 0')
            return redirect('product_detail', product_id=product_id)
        
        # Check if product is in stock
        if product.stock < quantity:
            messages.error(request, f'Not enough stock. Available: {product.stock}')
            return redirect('product_detail', product_id=product_id)
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if product is already in cart
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            # Update quantity
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            # Create new cart item
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
        
        messages.success(request, 'Product added to cart')
        return redirect('cart')
    
    return redirect('product_detail', product_id=product_id)

@login_required
def update_cart_item_view(request, item_id):
    if request.method == 'POST':
        # Get cart item
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        # Get quantity
        quantity = int(request.POST.get('quantity', 1))
        
        # Check if quantity is valid
        if quantity <= 0:
            messages.error(request, 'Quantity must be greater than 0')
            return redirect('cart')
        
        # Check if product is in stock
        if cart_item.product.stock < quantity:
            messages.error(request, f'Not enough stock. Available: {cart_item.product.stock}')
            return redirect('cart')
        
        # Update quantity
        cart_item.quantity = quantity
        cart_item.save()
        
        messages.success(request, 'Cart item updated')
        return redirect('cart')
    
    return redirect('cart')

@login_required
def remove_from_cart_view(request, item_id):
    # Get cart item
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    # Delete cart item
    cart_item.delete()
    
    messages.success(request, 'Product removed from cart')
    return redirect('cart')

@login_required
def clear_cart_view(request):
    # Get cart
    cart = get_object_or_404(Cart, user=request.user)
    
    # Delete all cart items
    CartItem.objects.filter(cart=cart).delete()
    
    messages.success(request, 'Cart cleared')
    return redirect('cart') 