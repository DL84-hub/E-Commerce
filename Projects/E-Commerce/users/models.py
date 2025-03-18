from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('store_owner', 'Store Owner'),
        ('customer', 'Customer'),
    )
    
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(unique=True, null=True, blank=True)
    email_verification_token_created = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def is_verification_token_valid(self):
        """Check if the verification token is still valid (within 24 hours)"""
        if not self.email_verification_token_created:
            return False
        return (timezone.now() - self.email_verification_token_created).total_seconds() <= 24 * 3600
        
    def generate_verification_token(self):
        """Generate a new verification token"""
        self.email_verification_token = uuid.uuid4()
        self.email_verification_token_created = timezone.now()
        self.save()
