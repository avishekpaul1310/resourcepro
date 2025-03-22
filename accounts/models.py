from django.db import models
from django.contrib.auth.models import User

# We'll use Django's built-in User model, but we can extend it if needed
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"