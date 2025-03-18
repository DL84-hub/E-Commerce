import unittest
import sys
import os

# Add the current directory to the path so that imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import test modules
from test_auth import AuthenticationTest
from test_products import ProductsTest
from test_stores import StoresTest
from test_cart_orders import CartOrdersTest
from test_api import APITest

if __name__ == "__main__":
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(AuthenticationTest))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(ProductsTest))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(StoresTest))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(CartOrdersTest))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(APITest))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful()) 