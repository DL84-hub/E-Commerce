from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Store
from .serializers import StoreSerializer, StoreCreateSerializer
from products.models import Product
from products.serializers import ProductSerializer
from .forms import StoreForm

# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny])
def store_list(request):
    stores = Store.objects.filter(is_verified=True)
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id, is_verified=True)
    serializer = StoreSerializer(store)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_store(request):
    # Check if user already has a store
    if hasattr(request.user, 'store'):
        return Response({'error': 'You already have a store'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user is a store owner
    if request.user.user_type != 'store_owner':
        return Response({'error': 'Only store owners can create stores'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = StoreCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        store = serializer.save()
        return Response({
            'message': 'Store created successfully',
            'store': StoreSerializer(store).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_store(request, store_id):
    # Check if store exists and user is the owner
    try:
        store = Store.objects.get(id=store_id, owner=request.user)
    except Store.DoesNotExist:
        return Response({'error': 'Store not found or you are not the owner'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StoreCreateSerializer(store, data=request.data, partial=True)
    if serializer.is_valid():
        store = serializer.save()
        return Response({
            'message': 'Store updated successfully',
            'store': StoreSerializer(store).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def store_dashboard(request, store_id):
    # Check if store exists and user is the owner
    try:
        store = Store.objects.get(id=store_id, owner=request.user)
    except Store.DoesNotExist:
        return Response({'error': 'Store not found or you are not the owner'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get store products
    products = Product.objects.filter(store=store)
    product_serializer = ProductSerializer(products, many=True)
    
    # Get store orders
    from orders.models import Order, OrderItem
    order_items = OrderItem.objects.filter(product__store=store)
    orders = Order.objects.filter(items__in=order_items).distinct()
    
    # Calculate total sales
    total_sales = sum(item.price * item.quantity for item in order_items)
    
    # Count orders by status
    order_status_counts = {
        'pending': orders.filter(status='pending').count(),
        'processing': orders.filter(status='processing').count(),
        'shipped': orders.filter(status='shipped').count(),
        'delivered': orders.filter(status='delivered').count(),
        'cancelled': orders.filter(status='cancelled').count(),
    }
    
    return Response({
        'store': StoreSerializer(store).data,
        'products_count': products.count(),
        'orders_count': orders.count(),
        'total_sales': total_sales,
        'order_status_counts': order_status_counts,
        'products': product_serializer.data
    })

# Frontend Views
def store_list_page(request):
    stores = Store.objects.filter(is_verified=True)
    return render(request, 'stores/store_list.html', {'stores': stores})

def store_detail_page(request, store_id):
    store = get_object_or_404(Store, id=store_id, is_verified=True)
    products = Product.objects.filter(store=store, is_active=True)
    
    # Get filter parameters
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort_by', 'newest')
    
    # Apply filters
    if category_id:
        products = products.filter(category_id=category_id)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')
    
    context = {
        'store': store,
        'products': products,
        'category_id': category_id,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    
    return render(request, 'stores/store_detail.html', context)

@login_required
def store_dashboard_page(request):
    # Check if user is a store owner
    if request.user.user_type != 'store_owner':
        messages.error(request, 'Only store owners can access the store dashboard.')
        return redirect('home')
    
    # Check if user has a store
    if not hasattr(request.user, 'store'):
        return redirect('create_store')
    
    store = request.user.store
    
    # Get store products
    products = Product.objects.filter(store=store)
    
    # Get store orders
    from orders.models import Order, OrderItem
    order_items = OrderItem.objects.filter(product__store=store)
    orders = Order.objects.filter(items__in=order_items).distinct()
    
    # Calculate total sales
    total_sales = sum(item.price * item.quantity for item in order_items)
    
    # Count orders by status
    order_status_counts = {
        'pending': orders.filter(status='pending').count(),
        'processing': orders.filter(status='processing').count(),
        'shipped': orders.filter(status='shipped').count(),
        'delivered': orders.filter(status='delivered').count(),
        'cancelled': orders.filter(status='cancelled').count(),
    }
    
    context = {
        'store': store,
        'products': products,
        'orders': orders,
        'products_count': products.count(),
        'orders_count': orders.count(),
        'total_sales': total_sales,
        'order_status_counts': order_status_counts,
    }
    
    return render(request, 'stores/store_dashboard.html', context)

@login_required
def create_store_page(request):
    # Check if user is a store owner
    if request.user.user_type != 'store_owner':
        messages.error(request, 'Only store owners can create stores.')
        return redirect('home')
    
    # Check if user already has a store
    if hasattr(request.user, 'store'):
        messages.info(request, 'You already have a store.')
        return redirect('store_dashboard')
    
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.is_verified = False  # Stores need to be verified by admin
            store.save()
            
            messages.success(request, 'Your store has been created and is pending verification.')
            return redirect('store_dashboard')
    else:
        form = StoreForm()
    
    return render(request, 'stores/create_store.html', {'form': form})
