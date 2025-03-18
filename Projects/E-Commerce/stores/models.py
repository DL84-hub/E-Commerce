from django.db import models
from users.models import User

class Store(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store')
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    logo = models.ImageField(upload_to='store_logos/', blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
