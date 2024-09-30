from django.db import models
from role.models import Role
from django.conf import settings

class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    full_name = models.CharField(max_length=255, blank=True, default='')
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    profile_picture_url = models.URLField(max_length=255, blank=True, default='')

    def __str__(self):
        return self.full_name or self.username

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default='')
    interests = models.TextField(blank=True, default='')
    learning_style = models.CharField(max_length=50, blank=True, default='')
    preferred_language = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return self.user.username

class UserPersonalization(models.Model):
    personalization_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommended_courses = models.TextField()  
    personalized_learning_path = models.TextField(blank=True, default='')  
    learning_style = models.CharField(max_length=50, blank=True, default='') 

    def __str__(self):
        return f"Personalization for {self.user.username}"
