import os
import sys
import django
import shutil
from pathlib import Path

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import models
from products.models import Product

def assign_product_images():
    # Get the base directory and image directories
    base_dir = Path(__file__).resolve().parent
    sports_images_dir = base_dir / 'sportsEquipments'
    media_dir = base_dir / 'media'
    product_images_dir = media_dir / 'product_images'
    
    # Create media directory if it doesn't exist
    if not product_images_dir.exists():
        os.makedirs(product_images_dir, exist_ok=True)
        print(f"Created directory: {product_images_dir}")
    
    # Define mappings from product names to image filenames
    image_mappings = [
        {"product_name": "Professional Basketball", "image_file": "Basketball.jpg"},
        {"product_name": "Yoga Mat", "image_file": "Yoga mat.jpg"},
        {"product_name": "Tennis Racket Pro", "image_file": "Tennis racket.jpg"},
        {"product_name": "Running Shoes", "image_file": "Running shoes.png"},
        {"product_name": "Fitness Tracker", "image_file": "Fitness Tracker.jpg"}
    ]
    
    # Process each mapping
    for mapping in image_mappings:
        product_name = mapping["product_name"]
        image_file = mapping["image_file"]
        
        print(f"\nProcessing product: {product_name}")
        
        # Get the product
        try:
            product = Product.objects.get(name=product_name)
            print(f"  Found product: {product.name} (ID: {product.id})")
        except Product.DoesNotExist:
            print(f"  Product not found: {product_name}")
            continue
        
        # Get the image file
        image_path = sports_images_dir / image_file
        if not image_path.exists():
            print(f"  Image file not found: {image_path}")
            continue
        
        print(f"  Found image file: {image_file}")
        
        # Copy the image to the media directory
        dest_path = product_images_dir / image_file
        
        try:
            # Copy the image file
            shutil.copy2(image_path, dest_path)
            print(f"  Copied {image_file} to {dest_path}")
            
            # Update the product's image field
            relative_path = f"product_images/{image_file}"
            product.image = relative_path
            product.save()
            
            print(f"  Updated product '{product.name}' with image '{image_file}'")
        except Exception as e:
            print(f"  Error copying image for {product.name}: {e}")
    
    print("\nProduct image assignment completed!")

if __name__ == "__main__":
    assign_product_images() 