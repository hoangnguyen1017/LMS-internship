# Generated by Django 5.1.1 on 2024-11-08 14:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0009_readingmaterial_pdf_file_alter_course_published_and_more'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('enrolled_courses', models.ManyToManyField(blank=True, related_name='students', to='course.course')),
                ('taught_courses', models.ManyToManyField(blank=True, related_name='instructors', to='course.course')),
            ],
        ),
    ]