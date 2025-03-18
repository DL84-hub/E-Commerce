import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import models
from products.models import Product, Category

def check_product_images():
    # Get all sports products
    sports_category = Category.objects.get(slug='sports')
    sports_products = Product.objects.filter(category=sports_category)
    
    print(f"Found {sports_products.count()} sports products:")
    for product in sports_products:
        print(f"  - {product.name} (ID: {product.id})")
        print(f"    Image field: {product.image}")
        if product.image:
            print(f"    Image URL: {product.image.url}")
        else:
            print(f"    Image URL: None")
        print()

if __name__ == "__main__":
    check_product_images() 