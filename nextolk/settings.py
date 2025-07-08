    # next_tiktok/settings.py (UPDATED: S3 Storage Configuration)

    from pathlib import Path
    import os
    import environ
    import dj_database_url

    # Initialize environment
    env = environ.Env(
        DEBUG=(bool, False),
        DATABASE_URL=(str, 'sqlite:///db.sqlite3'),
        SECRET_KEY=(str, 'unsafe-secret-key'),
        RENDER=(bool, False),
        AWS_ACCESS_KEY_ID=(str, ''), # NEW: Default empty
        AWS_SECRET_ACCESS_KEY=(str, ''), # NEW: Default empty
        AWS_STORAGE_BUCKET_NAME=(str, ''), # NEW: Default empty
        AWS_S3_REGION_NAME=(str, 'us-east-1'), # NEW: Default AWS region (change to yours)
        AWS_S3_CUSTOM_DOMAIN=(str, ''), # NEW: For custom domain if you use one
    )

    # Load .env file if present
    BASE_DIR = Path(__file__).resolve().parent.parent
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

    SECRET_KEY = env('SECRET_KEY')
    DEBUG = env('DEBUG')
    RENDER = env('RENDER')

    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
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
        'storages', # NEW: Add django-storages
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

    # Database
    DATABASES = {
        'default': env.db()
    }
    if not RENDER and not os.environ.get('DATABASE_URL'):
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }

    # Static files
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    # Media files (S3 Configuration)
    # Only use S3 when deployed on Render (or if AWS credentials are provided)
    if RENDER or (env('AWS_ACCESS_KEY_ID') and env('AWS_SECRET_ACCESS_KEY') and env('AWS_STORAGE_BUCKET_NAME')):
        AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
        AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
        AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')
        AWS_S3_FILE_OVERWRITE = False # Don't overwrite files with the same name
        AWS_DEFAULT_ACL = 'public-read' # Make uploaded files publicly readable
        AWS_QUERYSTRING_AUTH = False # Don't add query string authentication to URLs
        AWS_S3_VERIFY_SSL = True
        DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/media/' # NEW: S3 media URL
        # If you have a custom domain for S3 (e.g., CDN), uncomment and set this:
        # AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN')
        # MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    else:
        # Local development settings for media files
        MEDIA_URL = '/media/'
        MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')


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
    