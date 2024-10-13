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

    def __str__(self):
        return self.role_name