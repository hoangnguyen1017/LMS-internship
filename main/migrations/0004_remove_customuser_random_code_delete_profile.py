# Generated by Django 5.1.1 on 2024-10-12 07:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_customuser_random_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='random_code',
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
