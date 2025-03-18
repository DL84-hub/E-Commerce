import os
import sys
import django
import random
from pathlib import Path

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import models
from products.models import Product, Category

def update_product_images():
    # Get all sports products
    sports_category = Category.objects.get(slug='sports')
    sports_products = Product.objects.filter(category=sports_category)
    
    # Get all image files from the media/product_images directory
    base_dir = Path(__file__).resolve().parent
    product_images_dir = base_dir / 'media' / 'product_images'
    image_files = list(product_images_dir.glob('*.jpg'))
    
    if not image_files:
        print("No image files found in media/product_images directory")
        return
    
    print(f"Found {len(image_files)} image files")
    print(f"Found {sports_products.count()} sports products")
    
    # Update each sports product with a random image
    for i, product in enumerate(sports_products):
        # Select an image (cycling through available images if needed)
        image_index = i % len(image_files)
        image_file = image_files[image_index]
        
        # Update the product's image field
        relative_path = f"product_images/{image_file.name}"
        product.image = relative_path
        product.save()
        
        print(f"Updated product '{product.name}' with image '{image_file.name}'")
    
    print("Product image update completed!")

if __name__ == "__main__":
    update_product_images() 