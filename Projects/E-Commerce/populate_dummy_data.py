import os
import sys
import django
import random
import shutil
from django.core.files import File
from django.utils.text import slugify
from django.db import transaction
from django.contrib.auth import get_user_model
from pathlib import Path

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import models
from products.models import Category, Product
from stores.models import Store
from users.models import User

# Create categories
def create_categories():
    categories = [
        {
            'name': 'Sports',
            'description': 'Sports equipment and accessories for all types of sports and outdoor activities.',
            'slug': 'sports'
        },
        {
            'name': 'Education',
            'description': 'Books, stationery, and educational materials for students and professionals.',
            'slug': 'education'
        },
        {
            'name': 'Clothing',
            'description': 'Fashion apparel for men, women, and children including casual, formal, and sportswear.',
            'slug': 'clothing'
        },
        {
            'name': 'Electronics',
            'description': 'Electronic devices, gadgets, and accessories for home and personal use.',
            'slug': 'electronics'
        },
        {
            'name': 'Medical',
            'description': 'Healthcare products, medical supplies, and wellness items for personal care.',
            'slug': 'medical'
        }
    ]
    
    created_categories = []
    for category_data in categories:
        category, created = Category.objects.get_or_create(
            slug=category_data['slug'],
            defaults={
                'name': category_data['name'],
                'description': category_data['description']
            }
        )
        created_categories.append(category)
        print(f"Category {'created' if created else 'already exists'}: {category.name}")
    
    return created_categories

# Create store owners and stores
def create_stores(categories):
    stores_data = [
        {
            'owner': {
                'username': 'sportshop',
                'email': 'sportshop@example.com',
                'password': 'Password123!',
                'user_type': 'store_owner',
                'phone_number': '555-123-4567',
                'address': '123 Sports Ave, Athletic City, AC 12345'
            },
            'store': {
                'name': 'Champion Sports',
                'description': 'Your one-stop shop for all sports equipment and accessories. We offer high-quality products for athletes of all levels.',
                'address': '123 Sports Ave, Athletic City, AC 12345',
                'phone_number': '555-123-4567',
                'email': 'info@championsports.com',
                'category': 'sports'
            }
        },
        {
            'owner': {
                'username': 'edustore',
                'email': 'edustore@example.com',
                'password': 'Password123!',
                'user_type': 'store_owner',
                'phone_number': '555-234-5678',
                'address': '456 Learning Ln, Knowledge Town, KT 23456'
            },
            'store': {
                'name': 'Smart Learning Center',
                'description': 'Providing educational materials and resources for students, teachers, and lifelong learners. From textbooks to digital learning tools.',
                'address': '456 Learning Ln, Knowledge Town, KT 23456',
                'phone_number': '555-234-5678',
                'email': 'contact@smartlearning.com',
                'category': 'education'
            }
        },
        {
            'owner': {
                'username': 'fashionista',
                'email': 'fashionista@example.com',
                'password': 'Password123!',
                'user_type': 'store_owner',
                'phone_number': '555-345-6789',
                'address': '789 Style St, Fashion City, FC 34567'
            },
            'store': {
                'name': 'Trendy Threads',
                'description': 'Stay stylish with our curated collection of clothing for all occasions. From casual everyday wear to elegant evening attire.',
                'address': '789 Style St, Fashion City, FC 34567',
                'phone_number': '555-345-6789',
                'email': 'hello@trendythreads.com',
                'category': 'clothing'
            }
        },
        {
            'owner': {
                'username': 'techguru',
                'email': 'techguru@example.com',
                'password': 'Password123!',
                'user_type': 'store_owner',
                'phone_number': '555-456-7890',
                'address': '101 Tech Blvd, Digital City, DC 45678'
            },
            'store': {
                'name': 'Tech Haven',
                'description': 'Discover the latest in technology and electronics. We offer a wide range of gadgets, devices, and accessories for tech enthusiasts.',
                'address': '101 Tech Blvd, Digital City, DC 45678',
                'phone_number': '555-456-7890',
                'email': 'support@techhaven.com',
                'category': 'electronics'
            }
        },
        {
            'owner': {
                'username': 'healthplus',
                'email': 'healthplus@example.com',
                'password': 'Password123!',
                'user_type': 'store_owner',
                'phone_number': '555-567-8901',
                'address': '202 Wellness Way, Healthy Heights, HH 56789'
            },
            'store': {
                'name': 'Wellness Pharmacy',
                'description': 'Your health is our priority. We provide quality medical supplies, over-the-counter medications, and wellness products for your healthcare needs.',
                'address': '202 Wellness Way, Healthy Heights, HH 56789',
                'phone_number': '555-567-8901',
                'email': 'care@wellnesspharmacy.com',
                'category': 'medical'
            }
        }
    ]
    
    created_stores = []
    for store_data in stores_data:
        # Get or create store owner
        try:
            owner = User.objects.get(username=store_data['owner']['username'])
            print(f"Store owner already exists: {owner.username}")
        except User.DoesNotExist:
            owner = User.objects.create_user(
                username=store_data['owner']['username'],
                email=store_data['owner']['email'],
                password=store_data['owner']['password'],
                user_type=store_data['owner']['user_type'],
                phone_number=store_data['owner']['phone_number'],
                address=store_data['owner']['address']
            )
            print(f"Store owner created: {owner.username}")
        
        # Get category
        category_slug = store_data['store']['category']
        category = next((c for c in categories if c.slug == category_slug), None)
        
        # Get or create store
        try:
            store = Store.objects.get(owner=owner)
            print(f"Store already exists: {store.name}")
        except Store.DoesNotExist:
            store = Store.objects.create(
                owner=owner,
                name=store_data['store']['name'],
                description=store_data['store']['description'],
                address=store_data['store']['address'],
                phone_number=store_data['store']['phone_number'],
                email=store_data['store']['email'],
                is_verified=True
            )
            print(f"Store created: {store.name}")
        
        created_stores.append((store, category))
    
    return created_stores

# Create products for each store
def create_products(stores_with_categories):
    # Get sports equipment images with absolute paths
    base_dir = Path(__file__).resolve().parent
    sports_images_dir = base_dir / 'sportsEquipments'
    
    # Check if the directory exists
    if not sports_images_dir.exists():
        print(f"Warning: Sports equipment directory not found at {sports_images_dir}")
        sports_images = []
    else:
        # Get all image files from the directory
        sports_images = [str(f) for f in sports_images_dir.glob('*.jpg')]
        print(f"Found {len(sports_images)} sports equipment images")
    
    # Create media directory if it doesn't exist
    media_dir = base_dir / 'media'
    product_images_dir = media_dir / 'product_images'
    if not product_images_dir.exists():
        os.makedirs(product_images_dir, exist_ok=True)
        print(f"Created directory: {product_images_dir}")
    
    # Create placeholder images for other categories
    placeholder_images = {
        'education': 'https://via.placeholder.com/500x500.png?text=Education+Product',
        'clothing': 'https://via.placeholder.com/500x500.png?text=Clothing+Product',
        'electronics': 'https://via.placeholder.com/500x500.png?text=Electronics+Product',
        'medical': 'https://via.placeholder.com/500x500.png?text=Medical+Product'
    }
    
    products_data = {
        'sports': [
            {
                'name': 'Professional Basketball',
                'description': 'Official size and weight basketball for indoor and outdoor play. Durable rubber construction with excellent grip.',
                'price': 2249.99,  # ₹2,249.99 (converted from $29.99)
                'stock': 50,
                'image_index': 0
            },
            {
                'name': 'Yoga Mat',
                'description': 'Non-slip yoga mat with alignment lines. Perfect for yoga, pilates, and floor exercises. Eco-friendly material.',
                'price': 1874.99,  # ₹1,874.99 (converted from $24.99)
                'stock': 35,
                'image_index': 1
            },
            {
                'name': 'Tennis Racket Pro',
                'description': 'Lightweight tennis racket with large sweet spot. Ideal for beginners and intermediate players.',
                'price': 5999.99,  # ₹5,999.99 (converted from $79.99)
                'stock': 20,
                'image_index': 2
            },
            {
                'name': 'Running Shoes',
                'description': 'Breathable running shoes with cushioned soles for maximum comfort and support during long runs.',
                'price': 6749.99,  # ₹6,749.99 (converted from $89.99)
                'stock': 30,
                'image_index': 3
            },
            {
                'name': 'Fitness Tracker',
                'description': 'Water-resistant fitness tracker that monitors steps, heart rate, sleep, and more. Compatible with iOS and Android.',
                'price': 3749.99,  # ₹3,749.99 (converted from $49.99)
                'stock': 25,
                'image_index': 4
            }
        ],
        'education': [
            {
                'name': 'Complete Mathematics Textbook',
                'description': 'Comprehensive mathematics textbook covering algebra, geometry, calculus, and statistics. Includes practice problems and solutions.',
                'price': 2999.99,  # ₹2,999.99 (converted from $39.99)
                'stock': 40
            },
            {
                'name': 'Scientific Calculator',
                'description': 'Advanced scientific calculator with 240+ functions. Perfect for students in high school and college.',
                'price': 1499.99,  # ₹1,499.99 (converted from $19.99)
                'stock': 60
            },
            {
                'name': 'World History Encyclopedia',
                'description': 'Illustrated encyclopedia covering world history from ancient civilizations to modern times. Great reference for students of all ages.',
                'price': 3749.99,  # ₹3,749.99 (converted from $49.99)
                'stock': 25
            },
            {
                'name': 'Premium Notebook Set',
                'description': 'Set of 5 college-ruled notebooks with durable covers and perforated pages. Ideal for students and professionals.',
                'price': 1124.99,  # ₹1,124.99 (converted from $14.99)
                'stock': 100
            },
            {
                'name': 'Digital Language Learning Software',
                'description': 'Language learning software with courses in 24 languages. Features speech recognition and adaptive learning technology.',
                'price': 4499.99,  # ₹4,499.99 (converted from $59.99)
                'stock': 15
            }
        ],
        'clothing': [
            {
                'name': 'Classic Denim Jeans',
                'description': 'Timeless denim jeans with a comfortable fit. Available in multiple washes and sizes.',
                'price': 3749.99,  # ₹3,749.99 (converted from $49.99)
                'stock': 75
            },
            {
                'name': 'Cotton T-Shirt Pack',
                'description': 'Pack of 3 premium cotton t-shirts. Soft, breathable, and perfect for everyday wear.',
                'price': 2249.99,  # ₹2,249.99 (converted from $29.99)
                'stock': 50
            },
            {
                'name': 'Winter Jacket',
                'description': 'Insulated winter jacket with water-resistant outer shell. Keeps you warm in cold weather conditions.',
                'price': 6749.99,  # ₹6,749.99 (converted from $89.99)
                'stock': 30
            },
            {
                'name': 'Formal Dress Shirt',
                'description': 'Wrinkle-resistant formal shirt for professional settings. Available in various colors and sizes.',
                'price': 2999.99,  # ₹2,999.99 (converted from $39.99)
                'stock': 40
            },
            {
                'name': 'Athletic Leggings',
                'description': 'High-waisted athletic leggings with moisture-wicking fabric. Perfect for workouts and casual wear.',
                'price': 2624.99,  # ₹2,624.99 (converted from $34.99)
                'stock': 60
            }
        ],
        'electronics': [
            {
                'name': 'Wireless Bluetooth Headphones',
                'description': 'Over-ear wireless headphones with noise cancellation and 30-hour battery life. Crystal clear sound quality.',
                'price': 9749.99,  # ₹9,749.99 (converted from $129.99)
                'stock': 35
            },
            {
                'name': 'Smart Home Speaker',
                'description': 'Voice-controlled smart speaker with virtual assistant. Controls smart home devices and plays music from streaming services.',
                'price': 5999.99,  # ₹5,999.99 (converted from $79.99)
                'stock': 25
            },
            {
                'name': 'Ultra HD 4K Monitor',
                'description': '27-inch 4K monitor with HDR support. Perfect for gaming, content creation, and professional work.',
                'price': 22499.99,  # ₹22,499.99 (converted from $299.99)
                'stock': 15
            },
            {
                'name': 'Portable Power Bank',
                'description': '20000mAh power bank with fast charging capability. Charges multiple devices simultaneously.',
                'price': 3749.99,  # ₹3,749.99 (converted from $49.99)
                'stock': 50
            },
            {
                'name': 'Wireless Gaming Mouse',
                'description': 'Ergonomic wireless gaming mouse with programmable buttons and adjustable DPI. Low latency for competitive gaming.',
                'price': 4499.99,  # ₹4,499.99 (converted from $59.99)
                'stock': 30
            }
        ],
        'medical': [
            {
                'name': 'Digital Blood Pressure Monitor',
                'description': 'Accurate blood pressure monitor with large display. Stores readings for multiple users and detects irregular heartbeats.',
                'price': 2999.99,  # ₹2,999.99 (converted from $39.99)
                'stock': 40
            },
            {
                'name': 'First Aid Kit',
                'description': 'Comprehensive first aid kit with 100+ items. Includes bandages, antiseptics, medications, and emergency tools.',
                'price': 2249.99,  # ₹2,249.99 (converted from $29.99)
                'stock': 60
            },
            {
                'name': 'Digital Thermometer',
                'description': 'Fast-reading digital thermometer with fever alert. Suitable for oral, rectal, and underarm use.',
                'price': 974.99,  # ₹974.99 (converted from $12.99)
                'stock': 75
            },
            {
                'name': 'Vitamin D Supplements',
                'description': '90-day supply of Vitamin D3 supplements. Supports bone health, immune function, and overall wellness.',
                'price': 1499.99,  # ₹1,499.99 (converted from $19.99)
                'stock': 100
            },
            {
                'name': 'Pulse Oximeter',
                'description': 'Fingertip pulse oximeter that measures blood oxygen levels and pulse rate. Compact and easy to use.',
                'price': 1874.99,  # ₹1,874.99 (converted from $24.99)
                'stock': 50
            }
        ]
    }
    
    created_products = []
    for store, category in stores_with_categories:
        category_slug = category.slug
        if category_slug in products_data:
            for product_data in products_data[category_slug]:
                # Check if product already exists
                existing_product = Product.objects.filter(
                    store=store,
                    name=product_data['name']
                ).first()
                
                if existing_product:
                    print(f"Product already exists: {existing_product.name} - {store.name}")
                    created_products.append(existing_product)
                    continue
                
                # Create new product
                try:
                    product = Product.objects.create(
                        store=store,
                        category=category,
                        name=product_data['name'],
                        description=product_data['description'],
                        price=product_data['price'],
                        stock=product_data['stock'],
                        is_active=True,
                        # Set a default image field value or leave it blank if allowed
                        image='product_images/default.jpg'  # Default image
                    )
                    
                    # If this is a sports product and we have images available
                    if category_slug == 'sports' and sports_images:
                        try:
                            # Get the image path based on the index
                            image_index = product_data.get('image_index', 0) % len(sports_images)
                            image_path = sports_images[image_index]
                            
                            # Check if the image file exists
                            if os.path.exists(image_path):
                                # Get the destination path
                                image_name = os.path.basename(image_path)
                                dest_path = os.path.join(product_images_dir, image_name)
                                
                                # Copy the image file to the media directory
                                shutil.copy2(image_path, dest_path)
                                
                                # Update the product's image field
                                relative_path = os.path.join('product_images', image_name)
                                product.image = relative_path
                                product.save()
                                
                                print(f"Added image {image_name} to product {product.name}")
                            else:
                                print(f"Image file not found: {image_path}")
                        except Exception as e:
                            print(f"Error adding image to product {product.name}: {e}")
                    
                    print(f"Product created: {product.name} - {store.name}")
                    created_products.append(product)
                except Exception as e:
                    print(f"Error creating product {product_data['name']}: {e}")
    
    return created_products

# Create customer accounts
def create_customers():
    customers_data = [
        {
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'Password123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '555-111-2222',
            'address': '123 Main St, Anytown, AT 12345'
        },
        {
            'username': 'janedoe',
            'email': 'janedoe@example.com',
            'password': 'Password123!',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone_number': '555-222-3333',
            'address': '456 Oak Ave, Somewhere, SW 23456'
        },
        {
            'username': 'bobsmith',
            'email': 'bobsmith@example.com',
            'password': 'Password123!',
            'first_name': 'Bob',
            'last_name': 'Smith',
            'phone_number': '555-333-4444',
            'address': '789 Pine Rd, Nowhere, NW 34567'
        },
        {
            'username': 'alicejones',
            'email': 'alicejones@example.com',
            'password': 'Password123!',
            'first_name': 'Alice',
            'last_name': 'Jones',
            'phone_number': '555-444-5555',
            'address': '101 Maple Dr, Everywhere, EW 45678'
        },
        {
            'username': 'mikebrown',
            'email': 'mikebrown@example.com',
            'password': 'Password123!',
            'first_name': 'Mike',
            'last_name': 'Brown',
            'phone_number': '555-555-6666',
            'address': '202 Cedar Ln, Anywhere, AW 56789'
        }
    ]
    
    created_customers = []
    for customer_data in customers_data:
        # Check if customer already exists
        try:
            customer = User.objects.get(username=customer_data['username'])
            print(f"Customer already exists: {customer.username}")
        except User.DoesNotExist:
            # Create new customer
            customer = User.objects.create_user(
                username=customer_data['username'],
                email=customer_data['email'],
                password=customer_data['password'],
                first_name=customer_data['first_name'],
                last_name=customer_data['last_name'],
                user_type='customer',
                phone_number=customer_data['phone_number'],
                address=customer_data['address']
            )
            print(f"Customer created: {customer.username}")
        
        created_customers.append(customer)
    
    return created_customers

# Main function to populate the database
@transaction.atomic
def populate_database():
    print("Starting database population...")
    
    # Create categories
    categories = create_categories()
    
    # Create stores
    stores_with_categories = create_stores(categories)
    
    # Create products
    products = create_products(stores_with_categories)
    
    # Create customers
    customers = create_customers()
    
    print("\nDatabase population completed!")
    print(f"Created {len(categories)} categories")
    print(f"Created {len(stores_with_categories)} stores")
    print(f"Created {len(products)} products")
    print(f"Created {len(customers)} customers")

if __name__ == "__main__":
    populate_database() 