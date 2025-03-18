import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import models
from products.models import Product, Category

def list_products():
    # Get all categories
    categories = Category.objects.all()
    
    for category in categories:
        print(f"\nCategory: {category.name}")
        products = Product.objects.filter(category=category)
        
        if products.exists():
            for product in products:
                print(f"  - {product.name} (Store: {product.store.name}, Image: {product.image})")
        else:
            print("  No products in this category")

if __name__ == "__main__":
    list_products() 