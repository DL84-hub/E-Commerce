import unittest
import requests
import json
import random
import string

def random_string(length=8):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

class APITest(unittest.TestCase):
    """Test API endpoints"""
    
    BASE_URL = "http://localhost:8000/api"
    
    def setUp(self):
        """Set up the test session and create a test user"""
        self.session = requests.Session()
        
        # Register a test user for API testing
        self.username = f"testapi_{random_string()}"
        self.email = f"{self.username}@example.com"
        self.password = "TestPassword123!"
        
        # Register via the API
        self.register_user()
        
        # Login to get session cookie
        self.login()
    
    def tearDown(self):
        """Close the test session"""
        self.session.close()
    
    def register_user(self):
        """Register a new user via the API"""
        url = f"{self.BASE_URL}/users/register/"
        data = {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "user_type": "customer"
        }
        
        response = self.session.post(url, data=data)
        return response
    
    def login(self):
        """Login via the API"""
        url = f"{self.BASE_URL}/users/login/"
        data = {
            "username": self.username,
            "password": self.password
        }
        
        response = self.session.post(url, data=data)
        return response
    
    def test_user_api(self):
        """Test user-related API endpoints"""
        # Test user profile endpoint
        url = f"{self.BASE_URL}/users/profile/"
        response = self.session.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], self.username)
        self.assertEqual(data["email"], self.email)
    
    def test_products_api(self):
        """Test product-related API endpoints"""
        # Test product list endpoint
        url = f"{self.BASE_URL}/products/"
        response = self.session.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
        # Test product detail endpoint if products exist
        if data:
            product_id = data[0]["id"]
            url = f"{self.BASE_URL}/products/{product_id}/"
            response = self.session.get(url)
            
            self.assertEqual(response.status_code, 200)
            product_data = response.json()
            self.assertEqual(product_data["id"], product_id)
        
        # Test product search endpoint
        url = f"{self.BASE_URL}/products/search/?q=test"
        response = self.session.get(url)
        
        self.assertEqual(response.status_code, 200)
        search_data = response.json()
        self.assertIsInstance(search_data, list)
    
    def test_stores_api(self):
        """Test store-related API endpoints"""
        # Test store list endpoint
        url = f"{self.BASE_URL}/stores/"
        response = self.session.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
        # Test store detail endpoint if stores exist
        if data:
            store_id = data[0]["id"]
            url = f"{self.BASE_URL}/stores/{store_id}/"
            response = self.session.get(url)
            
            self.assertEqual(response.status_code, 200)
            store_data = response.json()
            self.assertEqual(store_data["id"], store_id)
    
    def test_cart_api(self):
        """Test cart-related API endpoints"""
        # Test cart detail endpoint
        url = f"{self.BASE_URL}/cart/"
        response = self.session.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        
        # Test add to cart endpoint if products exist
        products_url = f"{self.BASE_URL}/products/"
        products_response = self.session.get(products_url)
        products_data = products_response.json()
        
        if products_data:
            product_id = products_data[0]["id"]
            url = f"{self.BASE_URL}/cart/add/"
            data = {
                "product_id": product_id,
                "quantity": 1
            }
            
            response = self.session.post(url, data=data)
            self.assertEqual(response.status_code, 200)
            
            # Test cart detail again to verify item was added
            url = f"{self.BASE_URL}/cart/"
            response = self.session.get(url)
            
            self.assertEqual(response.status_code, 200)
            cart_data = response.json()
            self.assertIn("items", cart_data)
            
            # Test remove from cart endpoint if items exist
            if cart_data["items"]:
                item_id = cart_data["items"][0]["id"]
                url = f"{self.BASE_URL}/cart/remove/{item_id}/"
                
                response = self.session.post(url)
                self.assertEqual(response.status_code, 200)
    
    def test_orders_api(self):
        """Test order-related API endpoints"""
        # Test order list endpoint
        url = f"{self.BASE_URL}/orders/"
        response = self.session.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
        # Test create order endpoint if products exist
        products_url = f"{self.BASE_URL}/products/"
        products_response = self.session.get(products_url)
        products_data = products_response.json()
        
        if products_data:
            # First add a product to cart
            product_id = products_data[0]["id"]
            cart_url = f"{self.BASE_URL}/cart/add/"
            cart_data = {
                "product_id": product_id,
                "quantity": 1
            }
            
            self.session.post(cart_url, data=cart_data)
            
            # Then create an order
            url = f"{self.BASE_URL}/orders/create/"
            order_data = {
                "shipping_address": "123 Test Street, Test City, Test Country"
            }
            
            response = self.session.post(url, data=order_data)
            
            # Status code might be 201 (Created) or 200 (OK)
            self.assertIn(response.status_code, [200, 201])
            
            # Test order detail endpoint if orders exist
            url = f"{self.BASE_URL}/orders/"
            response = self.session.get(url)
            orders_data = response.json()
            
            if orders_data:
                order_id = orders_data[0]["id"]
                url = f"{self.BASE_URL}/orders/{order_id}/"
                
                response = self.session.get(url)
                self.assertEqual(response.status_code, 200)
                order_data = response.json()
                self.assertEqual(order_data["id"], order_id)

if __name__ == "__main__":
    unittest.main() 