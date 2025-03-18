from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse

def send_verification_email(user, request):
    """Send verification email to user"""
    verification_url = request.build_absolute_uri(
        reverse('verify_email', kwargs={'token': str(user.email_verification_token)})
    )
    
    context = {
        'user': user,
        'verification_url': verification_url,
    }
    
    html_message = render_to_string('users/email/verify_email.html', context)
    
    send_mail(
        subject='Verify your email address - Local E-Commerce',
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    ) 