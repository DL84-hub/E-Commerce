from django.shortcuts import render
from products.models import Product, Category
from stores.models import Store

def home(request):
    # Get featured products (latest 8 active products)
    featured_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    # Get featured stores (latest 3 verified stores)
    featured_stores = Store.objects.filter(is_verified=True).order_by('-created_at')[:3]
    
    # Get all categories
    categories = Category.objects.all()
    
    context = {
        'featured_products': featured_products,
        'featured_stores': featured_stores,
        'categories': categories,
    }
    
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html') 