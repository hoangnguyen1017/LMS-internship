# Generated by Django 5.1.1 on 2024-10-26 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collaboration_group', '0003_initial'),
        ('course', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collaborationgroup',
            name='course',
        ),
        migrations.AddField(
            model_name='collaborationgroup',
            name='courses',
            field=models.ManyToManyField(related_name='collaboration_groups', to='course.course'),
        ),
    ]
