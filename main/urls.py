from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'main'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('', views.login_view, name='login'), 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    
]