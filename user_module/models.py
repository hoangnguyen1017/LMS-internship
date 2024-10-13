from django.db import models
from user.models import User  # Ensure User model path is correct
from module_group.models import Module  # Ensure Module model path is correct

class UserModule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'module')  # Ensures that a user-module combination is unique

    def __str__(self):
        return f"{self.user.username} - {self.module.module_name}"
