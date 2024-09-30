from django.urls import path
from . import views

app_name = 'subject'
urlpatterns = [
    path('', views.subject_list, name='subject_list'),
    path('add/', views.subject_add, name='subject_add'),
    path('subjects/edit/<int:pk>/', views.subject_edit, name='subject_edit'),
    path('subjects/delete/<int:pk>/', views.subject_delete, name='subject_delete'),
]


# urlpatterns = [
#     # Module Group URLs
#     path('', views.module_group_list, name='module_group_list'),
#     path('add/', views.module_group_add, name='module_group_add'),
#     path('<int:pk>/', views.module_group_detail, name='module_group_detail'),
#     path('<int:pk>/edit/', views.module_group_edit, name='module_group_edit'),
#     path('<int:pk>/delete/', views.module_group_delete, name='module_group_delete'),
    
#     # Module URLs
#     path('modules/', views.module_list, name='module_list'),
#     path('modules/add/', views.module_add, name='module_add'),
#     path('modules/<int:pk>/', views.module_detail, name='module_detail'),
#     path('modules/<int:pk>/edit/', views.module_edit, name='module_edit'),
#     path('modules/<int:pk>/delete/', views.module_delete, name='module_delete'),
# ]
