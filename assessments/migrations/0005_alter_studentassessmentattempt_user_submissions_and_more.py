# Generated by Django 5.0.9 on 2024-10-30 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0004_studentassessmentattempt_is_proctored_and_more'),
        ('exercises', '0004_alter_submission_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentassessmentattempt',
            name='user_submissions',
            field=models.ManyToManyField(blank=True, related_name='attempts', to='exercises.submission'),
        ),
        migrations.DeleteModel(
            name='UserSubmission',
        ),
    ]
