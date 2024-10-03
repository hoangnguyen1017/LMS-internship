from django.db import models
from django.contrib.auth.models import AbstractUser

class Role(models.Model):
    role_name = models.CharField(max_length=100)
    can_view_admin_dashboard = models.BooleanField(default=False)
    can_view_manager_dashboard = models.BooleanField(default=False)
    can_view_user_dashboard = models.BooleanField(default=False)
    can_edit_roles = models.BooleanField(default=False)  # Chỉ admin có thể chỉnh sửa vai trò
    can_view_users = models.BooleanField(default=False)  # Có thể xem danh sách người dùng
    can_edit_users = models.BooleanField(default=True)   # Có thể chỉnh sửa thông tin người dùng

    def __str__(self):
        return self.role_name

class CustomUser(AbstractUser):
    # Thêm các trường bổ sung tại đây
    bio = models.TextField(blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Thay đổi tên liên kết
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions '
                  'granted to each of their groups.',
        verbose_name='groups'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Thay đổi tên liên kết
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

