from django.db import models
from django.contrib.auth.models import Permission

class Role(models.Model):
    role_name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        help_text='Permissions assigned to this role.',
        verbose_name='permissions',
        related_name='role_permissions',
    )
    modules = models.ManyToManyField(
        'module_group.Module',  # Sử dụng tên chuỗi thay vì import
        blank=True,
        help_text='Modules assigned to this role.',
        verbose_name='modules',
        related_name='role_modules',
    )
    class Meta:
        default_permissions = () 
        permissions = [
            ('can_delete_user', 'Can delete user'),  # Thêm quyền xóa người dùng
            ('can_add_user', 'Can add user'),
            ('can_edit_user', 'Can edit user'),
            ('can_export_users', 'Can export users'),
            ('can_import_users', 'Can import users'),
            ('can_detail_user','Can detail user')
        ]

    def __str__(self):
        return self.role_name