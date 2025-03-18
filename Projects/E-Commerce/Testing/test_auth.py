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

class AuthenticationTest(BaseTest):
    """Test user authentication functionality"""
    
    def test_login_page_loads(self):
        """Test that the login page loads correctly"""
        self.navigate_to("/login/")
        
        # Check that the login form is displayed
        form = self.wait_for_element(By.TAG_NAME, "form")
        self.assertIsNotNone(form)
        
        # Check for username and password fields
        username_input = self.wait_for_element(By.NAME, "username")
        password_input = self.wait_for_element(By.NAME, "password")
        
        self.assertIsNotNone(username_input)
        self.assertIsNotNone(password_input)
    
    def test_register_page_loads(self):
        """Test that the registration page loads correctly"""
        self.navigate_to("/register/")
        
        # Check that the registration form is displayed
        form = self.wait_for_element(By.TAG_NAME, "form")
        self.assertIsNotNone(form)
        
        # Check for required fields
        username_input = self.wait_for_element(By.NAME, "username")
        email_input = self.wait_for_element(By.NAME, "email")
        password1_input = self.wait_for_element(By.NAME, "password1")
        password2_input = self.wait_for_element(By.NAME, "password2")
        
        self.assertIsNotNone(username_input)
        self.assertIsNotNone(email_input)
        self.assertIsNotNone(password1_input)
        self.assertIsNotNone(password2_input)
    
    def test_register_customer(self):
        """Test registering a new customer account"""
        username = f"testcustomer_{random_string()}"
        email = f"{username}@example.com"
        password = "TestPassword123!"
        
        success = self.register_user(username, email, password, user_type="customer")
        self.assertTrue(success, "Customer registration failed")
        
        # Check if we're redirected to the home page
        self.assertEqual(self.driver.current_url, self.get_url("/"))
        
        # Logout
        self.logout()
    
    def test_register_store_owner(self):
        """Test registering a new store owner account"""
        username = f"teststore_{random_string()}"
        email = f"{username}@example.com"
        password = "TestPassword123!"
        
        success = self.register_user(username, email, password, user_type="store_owner")
        self.assertTrue(success, "Store owner registration failed")
        
        # Check if we're redirected to the home page
        self.assertEqual(self.driver.current_url, self.get_url("/"))
        
        # Logout
        self.logout()
    
    def test_login_logout(self):
        """Test login and logout functionality"""
        # First register a new user
        username = f"testlogin_{random_string()}"
        email = f"{username}@example.com"
        password = "TestPassword123!"
        
        self.register_user(username, email, password)
        self.logout()
        
        # Now test login
        success = self.login(username, password)
        self.assertTrue(success, "Login failed")
        
        # Check if we're redirected to the home page
        self.assertEqual(self.driver.current_url, self.get_url("/"))
        
        # Test logout
        success = self.logout()
        self.assertTrue(success, "Logout failed")
        
        # Check if we're redirected to the home page
        self.assertEqual(self.driver.current_url, self.get_url("/"))
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        self.navigate_to("/login/")
        
        # Fill in the login form with invalid credentials
        username_input = self.wait_for_element(By.NAME, "username")
        password_input = self.wait_for_element(By.NAME, "password")
        
        username_input.send_keys("nonexistentuser")
        password_input.send_keys("wrongpassword")
        
        # Submit the form
        login_button = self.wait_for_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_button.click()
        
        # Wait for the page to refresh
        time.sleep(2)
        
        # Check for error message
        try:
            error_message = self.driver.find_element(By.CLASS_NAME, "alert-danger")
            self.assertIsNotNone(error_message, "Error message not displayed for invalid login")
        except:
            self.fail("Error message not displayed for invalid login")

if __name__ == "__main__":
    unittest.main() 