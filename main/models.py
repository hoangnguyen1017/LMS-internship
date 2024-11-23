from django.db import models
from django.conf import settings 
from django.contrib.auth.models import AbstractUser, Group, Permission


class Registration(models.Model):
    username = models.CharField(max_length=100)
    full_name = models.CharField(max_length=255, blank=True, default='')
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class CustomUser(AbstractUser):
    is_created_by_createsuperuser = models.BooleanField(default=False)
    full_name = models.CharField(max_length=255, blank=True, default='')
    random_code = models.CharField(max_length=10, blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
    )

    def __str__(self):
        return self.username

class SiteStatus(models.Model):
    status = models.BooleanField(default=True)  # True: Mở, False: Khóa

    def __str__(self):
        return "Mở" if self.status else "Khóa"
    

from django.db import models
from user.models import User
from django.utils import timezone
class PasswordChangeRecord(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    change_count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)  # Trường tự động cập nhật mỗi khi bản ghi được lưu

    def __str__(self):
        return f"{self.user.username} - Password change record"

    @classmethod
    def get_or_create_record(cls, user):
        """Lấy hoặc tạo bản ghi thay đổi mật khẩu cho người dùng."""
        record, created = cls.objects.get_or_create(user=user)
        return record

    def update_change_count(self):
        """Cập nhật số lần thay đổi mật khẩu."""
        self.change_count += 1
        self.save()

    def reset_change_count(self):
        """Đặt lại số lần thay đổi mật khẩu về 0."""
        self.change_count = 0
        self.save()