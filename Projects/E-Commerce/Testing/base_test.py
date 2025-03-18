import time
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class BaseTest(unittest.TestCase):
    """Base class for all Selenium tests"""
    
    BASE_URL = "http://localhost:8000"
    
    def setUp(self):
        """Set up the test driver"""
        chrome_options = Options()
        # Uncomment the line below to run tests in headless mode
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
    
    def tearDown(self):
        """Close the test driver"""
        if self.driver:
            self.driver.quit()
    
    def get_url(self, path):
        """Get the full URL for a given path"""
        return f"{self.BASE_URL}{path}"
    
    def navigate_to(self, path):
        """Navigate to a specific path"""
        self.driver.get(self.get_url(path))
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be visible"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.fail(f"Element {value} not visible after {timeout} seconds")
    
    def wait_for_element_clickable(self, by, value, timeout=10):
        """Wait for an element to be clickable"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            self.fail(f"Element {value} not clickable after {timeout} seconds")
    
    def login(self, username, password):
        """Login with the given credentials"""
        self.navigate_to("/login/")
        
        # Fill in the login form
        username_input = self.wait_for_element(By.NAME, "username")
        password_input = self.wait_for_element(By.NAME, "password")
        
        username_input.send_keys(username)
        password_input.send_keys(password)
        
        # Submit the form
        login_button = self.wait_for_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_button.click()
        
        # Wait for the redirect to complete
        time.sleep(2)
        
        # Check if login was successful
        try:
            self.driver.find_element(By.XPATH, "//a[contains(text(), 'Logout')]")
            return True
        except NoSuchElementException:
            return False
    
    def register_user(self, username, email, password, user_type="customer"):
        """Register a new user"""
        self.navigate_to("/register/")
        
        # Fill in the registration form
        username_input = self.wait_for_element(By.NAME, "username")
        email_input = self.wait_for_element(By.NAME, "email")
        password1_input = self.wait_for_element(By.NAME, "password1")
        password2_input = self.wait_for_element(By.NAME, "password2")
        
        username_input.send_keys(username)
        email_input.send_keys(email)
        password1_input.send_keys(password)
        password2_input.send_keys(password)
        
        # Select user type
        if user_type == "store_owner":
            store_owner_radio = self.wait_for_element(By.XPATH, "//input[@value='store_owner']")
            store_owner_radio.click()
        
        # Submit the form
        register_button = self.wait_for_element(By.XPATH, "//button[contains(text(), 'Register')]")
        register_button.click()
        
        # Wait for the redirect to complete
        time.sleep(2)
        
        # Check if registration was successful
        try:
            self.driver.find_element(By.XPATH, "//a[contains(text(), 'Logout')]")
            return True
        except NoSuchElementException:
            return False
    
    def logout(self):
        """Logout the current user"""
        try:
            logout_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Logout')]")
            logout_link.click()
            time.sleep(2)
            return True
        except NoSuchElementException:
            return False 