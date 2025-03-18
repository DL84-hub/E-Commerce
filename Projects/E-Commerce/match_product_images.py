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
from products.models import Product, Category

def match_product_images():
    # Get all sports products
    sports_category = Category.objects.get(slug='sports')
    sports_products = Product.objects.filter(category=sports_category)
    
    print(f"Found {sports_products.count()} sports products:")
    for product in sports_products:
        print(f"  - {product.name} (ID: {product.id})")
    
    # Get the base directory and image directories
    base_dir = Path(__file__).resolve().parent
    sports_images_dir = base_dir / 'sportsEquipments'
    media_dir = base_dir / 'media'
    product_images_dir = media_dir / 'product_images'
    
    # Create media directory if it doesn't exist
    if not product_images_dir.exists():
        os.makedirs(product_images_dir, exist_ok=True)
        print(f"Created directory: {product_images_dir}")
    
    # List all image files in the sportsEquipments directory
    image_files = list(sports_images_dir.glob('*.*'))
    print(f"Found {len(image_files)} image files in sportsEquipments directory:")
    for image_file in image_files:
        print(f"  - {image_file.name}")
    
    # Define direct mappings from product IDs to image filenames
    direct_mappings = {
        1: 'Basketball.jpg',        # Professional Basketball
        2: 'Yoga mat.jpg',          # Yoga Mat
        3: 'Tennis racket.jpg',     # Tennis Racket Pro
        4: 'Running shoes.png',     # Running Shoes
        5: 'Fitness Tracker.jpg'    # Fitness Tracker
    }
    
    print(f"Direct mappings: {direct_mappings}")
    
    # Match products with images
    for product in sports_products:
        print(f"\nProcessing product: {product.name} (ID: {product.id})")
        
        # Check if we have a direct mapping
        if product.id in direct_mappings:
            image_filename = direct_mappings[product.id]
            image_path = sports_images_dir / image_filename
            
            if image_path.exists():
                print(f"  Found direct mapping: ID {product.id} -> {image_filename}")
                image_file = image_path
            else:
                print(f"  Direct mapping file not found: {image_path}")
                continue
        else:
            print(f"  No direct mapping found for product ID {product.id}")
            continue
        
        # Copy the image to the media directory
        image_name = image_file.name
        dest_path = product_images_dir / image_name
        
        try:
            # Copy the image file
            shutil.copy2(image_file, dest_path)
            print(f"  Copied {image_file.name} to {dest_path}")
            
            # Update the product's image field
            relative_path = f"product_images/{image_name}"
            product.image = relative_path
            product.save()
            
            print(f"  Updated product '{product.name}' with image '{image_name}'")
        except Exception as e:
            print(f"  Error copying image for {product.name}: {e}")
    
    print("\nProduct image matching completed!")

if __name__ == "__main__":
    match_product_images() 