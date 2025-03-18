from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('create/', views.create_product, name='create_product'),
    path('<int:product_id>/update/', views.update_product, name='update_product'),
    path('<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
    path('search/', views.search_products, name='search_products'),
] 