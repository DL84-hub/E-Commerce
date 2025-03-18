from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Product, Category
from .serializers import ProductSerializer, ProductCreateSerializer, CategorySerializer

# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny])
def product_list(request):
    products = Product.objects.filter(is_active=True)
    
    # Filter by category
    category_id = request.query_params.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter by price range
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Filter by store
    store_id = request.query_params.get('store')
    if store_id:
        products = products.filter(store_id=store_id)
    
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    # Check if user is a store owner
    if request.user.user_type != 'store_owner':
        return Response({'error': 'Only store owners can create products'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ProductCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        product = serializer.save()
        return Response({
            'message': 'Product created successfully',
            'product': ProductSerializer(product).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request, product_id):
    # Check if product exists and user is the store owner
    try:
        product = Product.objects.get(id=product_id, store__owner=request.user)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found or you are not the owner'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProductCreateSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        product = serializer.save()
        return Response({
            'message': 'Product updated successfully',
            'product': ProductSerializer(product).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request, product_id):
    # Check if product exists and user is the store owner
    try:
        product = Product.objects.get(id=product_id, store__owner=request.user)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found or you are not the owner'}, status=status.HTTP_404_NOT_FOUND)
    
    product.is_active = False
    product.save()
    return Response({'message': 'Product deleted successfully'})

@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    serializer = CategorySerializer(category)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):
    query = request.query_params.get('q', '')
    if not query:
        return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    products = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query) |
        Q(category__name__icontains=query),
        is_active=True
    )
    
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# Frontend Views
def product_list_page(request):
    categories = Category.objects.all()
    
    # Get filter parameters
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort_by', 'newest')
    
    # Base query
    products = Product.objects.filter(is_active=True)
    
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
        'products': products,
        'categories': categories,
        'category_id': category_id,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    
    return render(request, 'products/product_list.html', context)

def product_detail_page(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Get related products (same category)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'products/product_detail.html', context)

def search_products_page(request):
    query = request.GET.get('q', '')
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query),
            is_active=True
        )
    else:
        products = Product.objects.none()
    
    context = {
        'products': products,
        'query': query,
    }
    
    return render(request, 'products/search_results.html', context)
