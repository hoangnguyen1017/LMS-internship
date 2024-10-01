"""
Django settings for lms_project project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
OPENAI_API_KEY = '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'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%9tkr6=2x0koih$(9^sggb-z)ub@g$37t*57u7eymim46k+9)w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = ['*']

CRISPY_TEMPLATE_PACK = 'bootstrap4'  # or 'bootstrap5'

# Cấu hình để chuyển hướng sau khi đăng nhập thành công
LOGIN_REDIRECT_URL = '/home'

# Cấu hình để chuyển hướng sau khi đăng xuất thành công
LOGOUT_REDIRECT_URL = '/'

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'main/static'),  # Thêm đường dẫn đến thư mục static của ứng dụng
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap4',
    'main',
    # 'question_bank', #remove
    'module_group',
    # 'module',
    'role',
    'user',
    'training_program',
    'subject',
    'training_program_subjects',
    'category',
    'question',
    # 'quiz',
    'user_module',
    'course'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lms_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lms_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'fsa_lms',
#         'USER': 'postgres',
#         'PASSWORD': '1234567890',
#         'HOST': 'localhost',  # Set to the appropriate host if using a remote server
#         'PORT': '5432',       # Default PostgreSQL port
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'fsa_lms',
#         'USER': 'ngattt@hcmuafserver',
#         'PASSWORD': 'fsa@123456',
#         'HOST': 'hcmuafserver.database.windows.net',  # Set to the appropriate host if using a remote server
#         'PORT': '1433',       # Default PostgreSQL port
#     }
# }



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hoang',
        'USER': 'root',
        'PASSWORD': '24635789asd',
        'HOST': 'localhost',
        'PORT': '3306',
    },
}



# //Driver={ODBC Driver 18 for SQL Server};Server=tcp:hcmuafserver.database.windows.net,1433;Database=hcmuafdb;Uid=ngattt;Pwd={your_password_here};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;

# jdbc:sqlserver://hcmuafserver.database.windows.net:1433;database=hcmuafdb;
# user=ngattt@hcmuafserver;password={your_password_here};encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.database.windows.net;loginTimeout=30;

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'FSA_indicateof',
#         'USER': 'FSA_indicateof',
#         'PASSWORD': '52eea5fe24803adf007d0b49ee538e3ee866a2e6',
#         'HOST': 'd0e.h.filess.io',
#         'PORT': '5433',
#         'OPTIONS': {
#             'options': '-c search_path=FSA_indicateof'  
#         }
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

