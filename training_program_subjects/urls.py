from django.urls import path
from . import views

app_name = 'training_program_subject'
urlpatterns = [
    path('training_program_subjects/', views.manage_subjects, name='training_program_subjects_form'),
]
