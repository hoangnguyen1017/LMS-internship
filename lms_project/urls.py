"""
URL configuration for lms_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from main.views import home

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', include('main.urls')),  # Include the URLs of the main app
    # path('module/', include('module.urls')),         # For module-related views
    path('module_group/', include('module_group.urls')),  
    path('user/', include('user.urls')),             # For user-related views
    path('user_module/', include('user_module.urls')), # For user-module assignments
    path('category/', include('category.urls')),  
    # path('question/', include('question.urls')),  
    # path('quiz/', include('quiz.urls')),  
    path('role/', include('role.urls')),  
    path('subject/', include('subject.urls')),  
    path('training_program/', include('training_program.urls')),  
    path('training_program_subjects/', include('training_program_subjects.urls')),  
    path('user/', include('user.urls')),  
    path('user_module/', include('user_module.urls')),
    path('courses/', include('course.urls')),
    # Add more paths for other new apps here

]




