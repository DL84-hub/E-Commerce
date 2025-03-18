from django.urls import path
from . import views as core_views
from users import views as user_views
from products import views as product_views
from stores import views as store_views
from orders import views as order_views
from cart import views as cart_views

urlpatterns = [
    # Home page
    path('', core_views.home, name='home'),
    
    # User authentication
    path('login/', user_views.login_page, name='login'),
    path('logout/', user_views.logout_page, name='logout'),
    path('register/', user_views.register_page, name='register'),
    path('profile/', user_views.profile_page, name='profile'),
    
    # Email verification
    path('verify-email/<str:token>/', user_views.verify_email_page, name='verify_email'),
    path('verify-email-sent/', user_views.verify_email_sent_page, name='verify_email_sent'),
    path('resend-verification/', user_views.resend_verification_page, name='resend_verification'),
    
    # Products
    path('products/', product_views.product_list_page, name='product_list'),
    path('products/<int:product_id>/', product_views.product_detail_page, name='product_detail'),
    path('products/search/', product_views.search_products_page, name='search_products'),
    
    # Stores
    path('stores/', store_views.store_list_page, name='store_list'),
    path('stores/<int:store_id>/', store_views.store_detail_page, name='store_detail'),
    path('store/dashboard/', store_views.store_dashboard_page, name='store_dashboard'),
    path('stores/create/', store_views.create_store_page, name='create_store'),
    
    # Orders and Cart
    path('cart/', cart_views.cart_page, name='cart'),
    path('cart/add/<int:product_id>/', cart_views.add_to_cart_view, name='add_to_cart'),
    path('cart/update/<int:item_id>/', cart_views.update_cart_item_view, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', cart_views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/clear/', cart_views.clear_cart_view, name='clear_cart'),
    path('checkout/', order_views.checkout_page, name='checkout'),
    path('orders/', order_views.order_list_page, name='order_list'),
    path('orders/<int:order_id>/', order_views.order_detail_page, name='order_detail'),
    
    # Static pages
    path('about/', core_views.about, name='about'),
] 