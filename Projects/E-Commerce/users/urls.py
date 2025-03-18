from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # API endpoints only
    path('register/', views.register, name='api_register'),
    path('login/', views.login_view, name='api_login'),
    path('logout/', views.logout_view, name='api_logout'),
    path('profile/', views.profile, name='api_profile'),
    path('profile/update/', views.update_profile, name='api_profile_update'),
    path('verify-email/<str:token>/', views.verify_email, name='api_verify_email'),
    path('resend-verification/', views.resend_verification_email, name='api_resend_verification'),
] 