# Generated by Django 5.0.9 on 2024-09-22 11:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPersonalization',
            fields=[
                ('personalization_id', models.AutoField(primary_key=True, serialize=False)),
                ('recommended_courses', models.TextField()),
                ('personalized_learning_path', models.TextField()),
                ('learning_style', models.CharField(max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
        ),
    ]
