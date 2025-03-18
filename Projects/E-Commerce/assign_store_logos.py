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
from stores.models import Store

def assign_store_logos():
    # Get the base directory and image directories
    base_dir = Path(__file__).resolve().parent
    media_dir = base_dir / 'media'
    store_logos_dir = media_dir / 'store_logos'
    
    # Create store_logos directory if it doesn't exist
    if not store_logos_dir.exists():
        os.makedirs(store_logos_dir, exist_ok=True)
        print(f"Created directory: {store_logos_dir}")
    
    # Get all stores
    stores = Store.objects.all()
    print(f"Found {stores.count()} stores:")
    for store in stores:
        print(f"  - {store.name} (ID: {store.id})")
    
    # Define mappings from store names to logo filenames
    # Assuming you have logo files with these names in the store_logos directory
    logo_mappings = {
        'Champion Sports': 'champion_sports.jpg',
        'Smart Learning Center': 'smart_learning_center.jpg',
        'Trendy Threads': 'trendy_threads.jpg',
        'Tech Haven': 'tech_haven.jpg',
        'Wellness Pharmacy': 'wellness_pharmacy.jpg'
    }
    
    # Process each store
    for store in stores:
        print(f"\nProcessing store: {store.name} (ID: {store.id})")
        
        # Check if we have a logo mapping for this store
        if store.name in logo_mappings:
            logo_filename = logo_mappings[store.name]
            logo_path = store_logos_dir / logo_filename
            
            # Check if the logo file exists
            if logo_path.exists():
                print(f"  Found logo file: {logo_filename}")
                
                # Update the store's logo field
                relative_path = f"store_logos/{logo_filename}"
                store.logo = relative_path
                store.save()
                
                print(f"  Updated store '{store.name}' with logo '{logo_filename}'")
            else:
                print(f"  Logo file not found: {logo_path}")
        else:
            print(f"  No logo mapping found for store: {store.name}")
    
    print("\nStore logo assignment completed!")

if __name__ == "__main__":
    assign_store_logos() 