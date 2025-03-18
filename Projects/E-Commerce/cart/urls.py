from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart_api'),
    path('add/', views.add_to_cart, name='add_to_cart_api'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item_api'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart_api'),
    path('clear/', views.clear_cart, name='clear_cart_api'),
] 