from django.urls import path
from . import views

urlpatterns = [
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quizzes/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('quizzes/create/', views.quiz_add, name='quiz_add'),
    path('quizzes/edit/<int:pk>/', views.quiz_edit, name='quiz_edit'),
    path('quizzes/delete/<int:pk>/', views.quiz_delete, name='quiz_delete'),
]
