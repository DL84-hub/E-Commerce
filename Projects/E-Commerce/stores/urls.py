from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    path('', views.store_list, name='store_list'),
    path('<int:store_id>/', views.store_detail, name='store_detail'),
    path('create/', views.create_store, name='create_store'),
    path('<int:store_id>/update/', views.update_store, name='update_store'),
    path('<int:store_id>/dashboard/', views.store_dashboard, name='store_dashboard'),
] 