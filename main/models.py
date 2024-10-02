from django.db import models


class Registration(models.Model):
    username = models.CharField(max_length=100)
    full_name = models.CharField(max_length=255, blank=True, default='')
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

