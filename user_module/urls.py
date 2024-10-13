from django.urls import path
from . import views

app_name = 'user_module'  # Ensure this is set

urlpatterns = [
    path('', views.user_module_list, name='user_module_list'),  # list view
    path('create/', views.user_module_create, name='user_module_create'),  # create view
    path('edit/<int:pk>/', views.user_module_edit, name='user_module_edit'),  # edit view
    path('delete/<int:pk>/', views.user_module_delete, name='user_module_delete'),  # delete view
]
