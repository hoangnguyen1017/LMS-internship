from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('course/add/', views.course_add, name='course_add'),
    path('course/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('course/<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('course/<int:course_id>/create_progress/', views.create_progress, name='create_progress'),
    path('course/<int:course_id>/update_progress_percentage/<int:user_id>/', views.update_progress_percentage, name='update_progress_percentage'),
]
