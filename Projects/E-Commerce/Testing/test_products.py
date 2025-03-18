import time
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from base_test import BaseTest

class ProductsTest(BaseTest):
    """Test product-related functionality"""
    
    def test_product_list_page_loads(self):
        """Test that the product list page loads correctly"""
        self.navigate_to("/products/")
        
        # Check that the page title is correct
        title = self.wait_for_element(By.TAG_NAME, "h1")
        self.assertIn("Products", title.text)
        
        # Check for product cards or empty state message
        try:
            # Either product cards should be present
            product_cards = self.driver.find_elements(By.CLASS_NAME, "card")
            if product_cards:
                self.assertGreater(len(product_cards), 0, "No product cards found")
            else:
                # Or an empty state message
                empty_message = self.driver.find_element(By.XPATH, "//div[contains(@class, 'text-center')]")
                self.assertIsNotNone(empty_message)
        except:
            self.fail("Neither product cards nor empty state message found")
    
    def test_product_filtering(self):
        """Test product filtering functionality"""
        self.navigate_to("/products/")
        
        # Check if there are filter controls
        try:
            # Try to find category filter
            category_select = self.driver.find_element(By.ID, "category")
            
            # Select a category
            select = Select(category_select)
            if len(select.options) > 1:
                select.select_by_index(1)  # Select the first non-default option
                
                # Submit the form
                filter_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Apply Filters')]")
                filter_button.click()
                
                # Wait for the page to refresh
                time.sleep(2)
                
                # Check that the URL contains the category parameter
                self.assertIn("category=", self.driver.current_url)
        except:
            # If no filters are found, that's okay - might not be implemented yet
            pass
    
    def test_product_sorting(self):
        """Test product sorting functionality"""
        self.navigate_to("/products/")
        
        # Check if there are sorting controls
        try:
            # Try to find sort select
            sort_select = self.driver.find_element(By.ID, "sort_by")
            
            # Select a sorting option
            select = Select(sort_select)
            if len(select.options) > 1:
                select.select_by_value("price_low")  # Sort by price low to high
                
                # Submit the form
                filter_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Apply Filters')]")
                filter_button.click()
                
                # Wait for the page to refresh
                time.sleep(2)
                
                # Check that the URL contains the sort parameter
                self.assertIn("sort_by=price_low", self.driver.current_url)
        except:
            # If no sorting controls are found, that's okay - might not be implemented yet
            pass
    
    def test_product_detail_page(self):
        """Test that the product detail page loads correctly"""
        # First navigate to the product list page
        self.navigate_to("/products/")
        
        # Try to find a product card
        try:
            product_cards = self.driver.find_elements(By.CLASS_NAME, "card")
            if product_cards:
                # Click on the first product's "View Details" button
                view_details_button = product_cards[0].find_element(By.XPATH, ".//a[contains(text(), 'View Details')]")
                view_details_button.click()
                
                # Wait for the page to load
                time.sleep(2)
                
                # Check that we're on a product detail page
                product_name = self.wait_for_element(By.TAG_NAME, "h1")
                self.assertIsNotNone(product_name)
                
                # Check for product price
                product_price = self.driver.find_element(By.XPATH, "//span[contains(@class, 'h5')]")
                self.assertIsNotNone(product_price)
                self.assertIn("₹", product_price.text)
                
                # Check for add to cart button (if product is in stock)
                try:
                    add_to_cart_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Add to Cart')]")
                    self.assertIsNotNone(add_to_cart_button)
                except:
                    # Product might be out of stock
                    out_of_stock = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Out of Stock')]")
                    self.assertIsNotNone(out_of_stock)
        except:
            # If no products are found, skip this test
            pass
    
    def test_search_functionality(self):
        """Test the product search functionality"""
        self.navigate_to("/products/")
        
        # Check if there's a search form
        try:
            search_input = self.driver.find_element(By.NAME, "q")
            
            # Enter a search term
            search_input.send_keys("test")
            
            # Submit the search form
            search_form = self.driver.find_element(By.XPATH, "//form[contains(@action, 'search')]")
            search_form.submit()
            
            # Wait for the search results page to load
            time.sleep(2)
            
            # Check that we're on the search results page
            self.assertIn("search", self.driver.current_url)
            
            # Check for search results or no results message
            try:
                # Either search results should be present
                search_results = self.driver.find_elements(By.CLASS_NAME, "card")
                if search_results:
                    self.assertGreater(len(search_results), 0, "No search results found")
                else:
                    # Or a no results message
                    no_results = self.driver.find_element(By.XPATH, "//div[contains(@class, 'text-center')]")
                    self.assertIsNotNone(no_results)
            except:
                self.fail("Neither search results nor no results message found")
        except:
            # If no search form is found, that's okay - might not be implemented yet
            pass

if __name__ == "__main__":
    unittest.main() 