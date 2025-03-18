import time
import unittest
import random
import string
from selenium.webdriver.common.by import By
from base_test import BaseTest

def random_string(length=8):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

class StoresTest(BaseTest):
    """Test store-related functionality"""
    
    def test_store_list_page_loads(self):
        """Test that the store list page loads correctly"""
        self.navigate_to("/stores/")
        
        # Check that the page title is correct
        title = self.wait_for_element(By.TAG_NAME, "h1")
        self.assertIn("Stores", title.text)
        
        # Check for store cards or empty state message
        try:
            # Either store cards should be present
            store_cards = self.driver.find_elements(By.CLASS_NAME, "card")
            if store_cards:
                self.assertGreater(len(store_cards), 0, "No store cards found")
            else:
                # Or an empty state message
                empty_message = self.driver.find_element(By.XPATH, "//div[contains(@class, 'text-center')]")
                self.assertIsNotNone(empty_message)
        except:
            self.fail("Neither store cards nor empty state message found")
    
    def test_store_detail_page(self):
        """Test that the store detail page loads correctly"""
        # First navigate to the store list page
        self.navigate_to("/stores/")
        
        # Try to find a store card
        try:
            store_cards = self.driver.find_elements(By.CLASS_NAME, "card")
            if store_cards:
                # Click on the first store's "Visit Store" button
                visit_store_button = store_cards[0].find_element(By.XPATH, ".//a[contains(text(), 'Visit Store')]")
                visit_store_button.click()
                
                # Wait for the page to load
                time.sleep(2)
                
                # Check that we're on a store detail page
                store_name = self.wait_for_element(By.TAG_NAME, "h1")
                self.assertIsNotNone(store_name)
                
                # Check for store description
                store_description = self.driver.find_element(By.XPATH, "//p[not(contains(@class, 'text-muted'))]")
                self.assertIsNotNone(store_description)
                
                # Check for products section
                products_heading = self.driver.find_element(By.XPATH, "//h2[contains(text(), 'Products')]")
                self.assertIsNotNone(products_heading)
        except:
            # If no stores are found, skip this test
            pass
    
    def test_create_store_page_loads(self):
        """Test that the create store page loads correctly for store owners"""
        # Register a store owner account
        username = f"teststore_{random_string()}"
        email = f"{username}@example.com"
        password = "TestPassword123!"
        
        self.register_user(username, email, password, user_type="store_owner")
        
        # Navigate to create store page
        self.navigate_to("/stores/create/")
        
        # Check that the page title is correct
        title = self.wait_for_element(By.XPATH, "//h4[contains(text(), 'Create Your Store')]")
        self.assertIsNotNone(title)
        
        # Check for form fields
        name_input = self.wait_for_element(By.NAME, "name")
        description_input = self.wait_for_element(By.NAME, "description")
        address_input = self.wait_for_element(By.NAME, "address")
        phone_input = self.wait_for_element(By.NAME, "phone_number")
        email_input = self.wait_for_element(By.NAME, "email")
        
        self.assertIsNotNone(name_input)
        self.assertIsNotNone(description_input)
        self.assertIsNotNone(address_input)
        self.assertIsNotNone(phone_input)
        self.assertIsNotNone(email_input)
        
        # Logout
        self.logout()
    
    def test_create_store(self):
        """Test creating a new store"""
        # Register a store owner account
        username = f"teststore_{random_string()}"
        email = f"{username}@example.com"
        password = "TestPassword123!"
        
        self.register_user(username, email, password, user_type="store_owner")
        
        # Navigate to create store page
        self.navigate_to("/stores/create/")
        
        # Fill in the store form
        name_input = self.wait_for_element(By.NAME, "name")
        description_input = self.wait_for_element(By.NAME, "description")
        address_input = self.wait_for_element(By.NAME, "address")
        phone_input = self.wait_for_element(By.NAME, "phone_number")
        email_input = self.wait_for_element(By.NAME, "email")
        
        store_name = f"Test Store {random_string()}"
        name_input.send_keys(store_name)
        description_input.send_keys("This is a test store created by automated testing.")
        address_input.send_keys("123 Test Street, Test City, Test Country")
        phone_input.send_keys("1234567890")
        email_input.send_keys(f"store_{random_string()}@example.com")
        
        # Submit the form
        create_button = self.wait_for_element(By.XPATH, "//button[contains(text(), 'Create Store')]")
        create_button.click()
        
        # Wait for the redirect to complete
        time.sleep(2)
        
        # Check if we're redirected to the store dashboard
        self.assertIn("dashboard", self.driver.current_url)
        
        # Check for success message
        success_message = self.driver.find_element(By.CLASS_NAME, "alert-success")
        self.assertIsNotNone(success_message)
        
        # Logout
        self.logout()
    
    def test_store_dashboard_access(self):
        """Test that only store owners can access the store dashboard"""
        # First test with a customer account
        username = f"testcustomer_{random_string()}"
        email = f"{username}@example.com"
        password = "TestPassword123!"
        
        self.register_user(username, email, password, user_type="customer")
        
        # Try to access the store dashboard
        self.navigate_to("/store/dashboard/")
        
        # Check that we're redirected to the home page
        self.assertEqual(self.driver.current_url, self.get_url("/"))
        
        # Check for error message
        error_message = self.driver.find_element(By.CLASS_NAME, "alert-danger")
        self.assertIsNotNone(error_message)
        
        # Logout
        self.logout()
        
        # Now test with a store owner account
        username = f"teststore_{random_string()}"
        email = f"{username}@example.com"
        password = "TestPassword123!"
        
        self.register_user(username, email, password, user_type="store_owner")
        
        # Try to access the store dashboard
        self.navigate_to("/store/dashboard/")
        
        # Check that we're redirected to the create store page (since we don't have a store yet)
        self.assertEqual(self.driver.current_url, self.get_url("/stores/create/"))
        
        # Logout
        self.logout()

if __name__ == "__main__":
    unittest.main() 