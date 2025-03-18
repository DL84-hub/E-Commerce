# E-Commerce Testing Suite

This directory contains automated tests for the E-Commerce platform. The tests cover both frontend functionality using Selenium and API endpoints using the requests library.

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure the E-Commerce application is running on `http://localhost:8000`.

3. Make sure you have Chrome browser installed (for Selenium tests).

## Running Tests

### Run All Tests

To run all tests:

```bash
python run_tests.py
```

### Run Specific Test Modules

To run specific test modules:

```bash
# Authentication tests
python test_auth.py

# Product tests
python test_products.py

# Store tests
python test_stores.py

# Cart and Order tests
python test_cart_orders.py

# API tests
python test_api.py
```

## Test Modules

### Authentication Tests (`test_auth.py`)

Tests user authentication functionality:
- Login page
- Registration page
- User registration (customer and store owner)
- Login and logout
- Invalid login

### Product Tests (`test_products.py`)

Tests product-related functionality:
- Product list page
- Product filtering
- Product sorting
- Product detail page
- Product search

### Store Tests (`test_stores.py`)

Tests store-related functionality:
- Store list page
- Store detail page
- Store creation
- Store dashboard access

### Cart and Order Tests (`test_cart_orders.py`)

Tests cart and order functionality:
- Cart page
- Adding products to cart
- Updating cart quantities
- Removing products from cart
- Checkout process
- Order list page
- Order detail page

### API Tests (`test_api.py`)

Tests API endpoints:
- User API (profile)
- Products API (list, detail, search)
- Stores API (list, detail)
- Cart API (detail, add, remove)
- Orders API (list, detail, create)

## Notes

- The tests are designed to be resilient to missing features or data. If a feature is not implemented or no data is available, the tests will skip or pass with appropriate messages.
- Some tests create test users and data, which may accumulate in the database over time. Consider cleaning up the database periodically.
- The tests assume a specific structure of HTML elements and CSS classes. If the frontend is significantly changed, the tests may need to be updated. 