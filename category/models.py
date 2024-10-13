from django.db import models
from subject.models import Subject

class Category(models.Model):
    category_name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return self.category_name
