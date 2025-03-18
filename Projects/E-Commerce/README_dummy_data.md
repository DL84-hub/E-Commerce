# Dummy Data Population Script

This script populates the Local E-Commerce database with dummy data for testing and demonstration purposes.

## What it creates:

1. **5 Categories**:
   - Sports
   - Education
   - Clothing
   - Electronics
   - Medical

2. **5 Stores** (one for each category):
   - Champion Sports (Sports)
   - Smart Learning Center (Education)
   - Trendy Threads (Clothing)
   - Tech Haven (Electronics)
   - Wellness Pharmacy (Medical)

3. **25 Products** (5 products per store)
   - Each product includes name, description, price, stock, and image

4. **5 Customer Accounts**:
   - John Doe
   - Jane Doe
   - Bob Smith
   - Alice Jones
   - Mike Brown

## Prerequisites

Make sure you have installed all the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Script

1. Make sure your Django project is properly configured and the database is set up.

2. Run the script from the project root directory:

```bash
python populate_dummy_data.py
```

3. The script will output progress information as it creates categories, stores, products, and customers.

## Notes

- The script uses the Unsplash API to download random images for products and store logos.
- All store owners and customers have the password `Password123!` for easy testing.
- The script is idempotent - running it multiple times will not create duplicate entries.
- All stores are marked as verified by default.

## Login Credentials

### Store Owners:
- Username: `sportshop`, Password: `Password123!`
- Username: `edustore`, Password: `Password123!`
- Username: `fashionista`, Password: `Password123!`
- Username: `techguru`, Password: `Password123!`
- Username: `healthplus`, Password: `Password123!`

### Customers:
- Username: `johndoe`, Password: `Password123!`
- Username: `janedoe`, Password: `Password123!`
- Username: `bobsmith`, Password: `Password123!`
- Username: `alicejones`, Password: `Password123!`
- Username: `mikebrown`, Password: `Password123!` 