# next_tiktok/settings.py (UPDATED: Fixed TEMPLATES BACKEND path)

from pathlib import Path
import os
import environ
import dj_database_url

# Initialize environment
env = environ.Env(
    DEBUG=(bool, True),
    DATABASE_URL=(str, 'postgresql://nextok_user:wpdIhw24W0dUKpabKn03raoDucF2mIHQ@dpg-d1o6o5jipnbc73ek7fa0-a/nextok'), # Ensure DATABASE_URL is expected as a string
    SECRET_KEY=(str, 'unsafe-secret-key'),
    CLOUDINARY_CLOUD_NAME=(str, 'du5z4g1jl'),
    CLOUDINARY_API_KEY=(str, '912456986662768'),
    CLOUDINARY_API_SECRET=(str, 'gduKAmp6kQy1H7BHYC9QNmwMPeU'),
    RENDER=(bool, False),
)

# Load .env file if present
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
RENDER = env('RENDER')

ALLOWED_HOSTS = ['localhost', '127.0.0.1'] # Corrected typo '127.00.1' to '127.0.0.1'
if RENDER:
    ALLOWED_HOSTS.append(env('RENDER_EXTERNAL_HOSTNAME'))

# Application definition
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
    'user',
    'eshop',
    'whitenoise.runserver_nostatic',
    'cloudinary',
    'django_cloudinary_storage', # Corrected app name here
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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
        'BACKEND': 'django.template.backends.django.DjangoTemplates', # <<< CORRECTED THIS LINE
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

# Database
DATABASES = {
    'default': env.db()
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (Cloudinary Configuration)
CLOUDINARY_CLOUD_NAME = env('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = env('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = env('CLOUDINARY_API_SECRET')

# Configure Cloudinary as the default file storage for media
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'

# Authentication
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

# CORS setup
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [
        'https://africana-1b1c6.web.app',
        'https://africana-1b1c6.firebaseapp.com',
        'https://nextolk.onrender.com',
    ]

# Jazzmin
JAZZMIN_SETTINGS = {
    "site_title": "Nextolke Admin",
    "site_header": "Nextolke",
    "welcome_sign_in": "Welcome to the Nextolke Admin",
    "copyright": "Copyright © 2025",
    "search_model": ["auth.User", "user.Video", "user.Profile"],
    "user_name_field": "username",
    "topbar_links": [
        {"name": "Home", "url": "admin:index", "new_window": False},
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "user.Video"},
        {"model": "user.Profile"},
        {"model": "eshop.Product"},
        {"model": "auth.User"},
    ],
    "order_with_respect_to": [
        "authtoken", "auth", "eshop", "user"
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",
        "user.Profile": "fas fa-id-card-alt",
        "user.Video": "fas fa-video",
        "user.Comment": "fas fa-comments",
        "user.Like": "fas fa-heart",
        "user.Follow": "fas fa-user-friends",
        "user.PhoneNumberOTP": "fas fa-sms",
        "eshop.Category": "fas fa-tags",
        "eshop.Product": "fas fa-box",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-white",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_explicit_toggle": True,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": True,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_button_classes": {
        "overflow_i": "btn-primary btn-sm",
        "all": "btn-primary btn-sm"
    }
}
