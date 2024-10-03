# models.py
from django.db import models

class Registration(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Mật khẩu đã mã hóa

    def __str__(self):
        return self.username