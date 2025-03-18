from django.urls import path
from core.views import home, about
from users.views import login_view, register_view, logout_view, profile_view
from products.views import product_list_page, product_detail_page, search_products_page
from stores.views import store_list_page, store_detail_page, store_dashboard_page, create_store_page
from orders.views import checkout_page, order_list_page, order_detail_page, create_order_view, update_order_status_view
from cart.views import cart_page, add_to_cart_view, update_cart_item_view, remove_from_cart_view, clear_cart_view

urlpatterns = [
    # Core URLs
    path('', home, name='home'),
    path('about/', about, name='about'),
    
    # User URLs
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    
    # Product URLs
    path('products/', product_list_page, name='product_list'),
    path('products/<int:product_id>/', product_detail_page, name='product_detail'),
    path('search/', search_products_page, name='search_products'),
    
    # Store URLs
    path('stores/', store_list_page, name='store_list'),
    path('stores/<int:store_id>/', store_detail_page, name='store_detail'),
    path('dashboard/', store_dashboard_page, name='store_dashboard'),
    path('stores/create/', create_store_page, name='create_store'),
    
    # Cart URLs
    path('cart/', cart_page, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart_view, name='add_to_cart'),
    path('cart/update/<int:item_id>/', update_cart_item_view, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', remove_from_cart_view, name='remove_from_cart'),
    path('cart/clear/', clear_cart_view, name='clear_cart'),
    
    # Order URLs
    path('checkout/', checkout_page, name='checkout'),
    path('orders/', order_list_page, name='order_list'),
    path('orders/<int:order_id>/', order_detail_page, name='order_detail'),
    path('orders/create/', create_order_view, name='create_order'),
    path('orders/<int:order_id>/update-status/', update_order_status_view, name='update_order_status'),
] 