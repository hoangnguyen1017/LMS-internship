from django.urls import path
from . import views

app_name = 'question'

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('<int:pk>/', views.question_detail, name='question_detail'),
    path('add/', views.question_add, name='question_add'),
    path('<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('<int:pk>/delete/', views.question_delete, name='question_delete'),
]
