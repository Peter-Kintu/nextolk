# next_tiktok/settings.py

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-fb$0_9g4c1m+m%2(l@r6_of6t@icf492vte4!j$*mydg$$@^=1'

DEBUG = False # Set to False for production on PythonAnywhere

# IMPORTANT: Set ALLOWED_HOSTS to your PythonAnywhere domain
ALLOWED_HOSTS = ['kintu2388.pythonanywhere.com', 'www.kintu2388.pythonanywhere.com']
# You can optionally keep your local development hosts if you plan to switch DEBUG back to True locally:
# ALLOWED_HOSTS = ['kintu2388.pythonanywhere.com', 'www.kintu2388.pythonanywhere.com', 'localhost', '127.0.0.1', '192.168.1.4']


INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'user', # Your user app
    'eshop', # Your eshop app
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Must be very high, preferably before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nextolk.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nextolk.wsgi.application'

# 🔄 MySQL Database Configuration (Keep your existing database config)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nextolk',
        'USER': 'nextolkuser',
        'PASSWORD': 'yourpassword',  # Replace with your real password
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = 'static/'

# The absolute path to the directory where collectstatic will gather static files for deployment.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (user-uploaded content like videos, profile pictures)
# The URL prefix for media files.
MEDIA_URL = '/media/'

# The absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# CORS settings for production. Initially, you might keep CORS_ALLOW_ALL_ORIGINS = True
# for testing, but for production, restrict it to your Firebase Hosting domain.
CORS_ALLOW_ALL_ORIGINS = True # For initial deployment, allows all origins.
# Once your Flutter app is deployed to Firebase, replace the above line with:
# CORS_ALLOW_ALL_ORIGINS = False
# CORS_ALLOWED_ORIGINS = [
#     "https://your-firebase-app-id.web.app", # Replace with your actual Firebase Hosting domain
#     "https://your-firebase-app-id.firebaseapp.com", # Replace with your actual Firebase Hosting domain
# ]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
