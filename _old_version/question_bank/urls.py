
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Add the 'home' view

# Training Program URLs
    path('training_programs/', views.training_program_list, name='training_program_list'),
    path('training_program/add/', views.training_program_add, name='training_program_add'),
    path('training_program/edit/<int:pk>/', views.training_program_edit, name='training_program_edit'),
    path('training_program/delete/<int:pk>/', views.training_program_delete, name='training_program_delete'),
    path('training_program/<int:program_id>/manage_subjects/', views.manage_subjects, name='training_program_manage_subjects'),
    
     
    # Subject URLs
    path('subjects/', views.subject_list, name='subject_list'),
    path('subject/add/', views.subject_add, name='subject_add'),
    path('subject/edit/<int:pk>/', views.subject_edit, name='subject_edit'),
    path('subject/delete/<int:pk>/', views.subject_delete, name='subject_delete'),

    # TrainingProgramSubjects URLs
    path('subjects/form/', views.training_program_subjects_add, name='training_program_subjects_form'),
    #========== USER
    path('users/', views.user_list, name='user_list'),
    path('user/<int:pk>/', views.user_detail, name='user_detail'),
    path('user/add/', views.user_add, name='user_add'),
    path('user/edit/<int:pk>/', views.user_edit, name='user_edit'),


    #========== ROLE
    path('roles/', views.role_list, name='role_list'),
    path('role/<int:pk>/', views.role_detail, name='role_detail'),  # Optional
    path('role/add/', views.role_add, name='role_add'),
    path('role/edit/<int:pk>/', views.role_edit, name='role_edit'),
    path('role/delete/<int:pk>/', views.role_delete, name='role_delete'),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    #========== QUIZ
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/add/', views.quiz_add, name='quiz_add'),
    path('quiz/<int:pk>/edit/', views.quiz_edit, name='quiz_edit'),
    path('quiz/<int:pk>/delete/', views.quiz_delete, name='quiz_delete'),

    #========== QUESTION
    path('questions/', views.question_list, name='question_list'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('question/add/', views.question_add, name='question_add'),
    path('question/<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('question/<int:question_pk>/answer/add/', views.answer_add, name='answer_add'),
    path('question/<int:pk>/delete/', views.question_delete, name='question_delete'),
    path('subject/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),

    #========== Module URLs
    path('modules/', views.module_list, name='module_list'),
    path('module/add/', views.module_add, name='module_add'),
    path('module/edit/<int:pk>/', views.module_edit, name='module_edit'),
    path('module/delete/<int:pk>/', views.module_delete, name='module_delete'),

    path('module_groups/', views.module_group_list, name='module_group_list'),
    path('module_groups/add/', views.module_group_add, name='module_group_add'),
    path('module_groups/edit/<int:pk>/', views.module_group_edit, name='module_group_edit'),
    path('module_groups/delete/<int:pk>/', views.module_group_delete, name='module_group_delete'),

    #==========UserModule URLs
    path('user-modules/', views.user_module_list, name='user_module_list'),
    path('user-module/add/', views.user_module_add, name='user_module_add'),
    path('user-module/edit/<int:pk>/', views.user_module_edit, name='user_module_edit'),
    path('user-module/delete/<int:pk>/', views.user_module_delete, name='user_module_delete'),

    # Subject URLs
    path('subjects/', views.subject_list, name='subject_list'),
    path('subject/add/', views.subject_add, name='subject_add'),
    path('subject/edit/<int:pk>/', views.subject_edit, name='subject_edit'),
    path('subject/delete/<int:pk>/', views.subject_delete, name='subject_delete'),

    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('category/add/', views.category_add, name='category_add'),
    path('category/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('category/delete/<int:pk>/', views.category_delete, name='category_delete'),
]

