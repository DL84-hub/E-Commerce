# Local E-Commerce Platform

A web-based e-commerce platform where local businesses can register, list their products, and sell online. Customers can browse products, add items to their cart, and make secure payments using Stripe API.

## Features

- User Authentication & Roles (Admin, Store Owners, Customers)
- Product Catalog Management
- Shopping Cart & Order Management
- Secure Payment Integration (Stripe)
- Admin Dashboard
- Store Owner Dashboard
- Customer Dashboard

## Tech Stack

- Backend: Django, Django REST Framework
- Frontend: HTML, CSS, Bootstrap, JavaScript
- Database: MySQL
- Payments: Stripe API
- Authentication: Django's built-in authentication system
- Deployment: AWS/Heroku

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a .env file with the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=mysql://user:password@localhost:3306/dbname
   STRIPE_PUBLIC_KEY=your-stripe-public-key
   STRIPE_SECRET_KEY=your-stripe-secret-key
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_STORAGE_BUCKET_NAME=your-bucket-name
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
ecommerce/
├── manage.py
├── requirements.txt
├── .env
├── core/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── stores/
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── products/
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── orders/
│   ├── models.py
│   ├── views.py
│   └── urls.py
└── static/
    ├── css/
    ├── js/
    └── images/
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 