# Generated by Django 5.1.1 on 2024-11-13 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_profile_is_locked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='is_locked',
        ),
        migrations.AddField(
            model_name='user',
            name='is_locked',
            field=models.BooleanField(default=False),
        ),
    ]