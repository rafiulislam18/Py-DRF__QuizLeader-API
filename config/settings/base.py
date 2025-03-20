import os
from pathlib import Path
from datetime import timedelta


BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party packages
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',  # Special to blacklist refresh tokens after rotation or logged out
    'drf_yasg',  # Swagger

    # Custom apps
    'apps.authentication',
    'apps.quiz',
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

ROOT_URLCONF = 'config.urls'
AUTH_USER_MODEL = 'authentication.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Use Simple JWT
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,  # Issues a new refresh token on each refresh
    'BLACKLIST_AFTER_ROTATION': True,  # Blacklists old refresh tokens
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': None,  # Use Django's SECRET_KEY for signing & config this later on separate environment-specific settings files due to security reasons
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',  # In-memory cache
        'LOCATION': 'quizLeaderAPI-cache',  # A unique identifier for the cache (can be anything for django default cache)
    }
}

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

WSGI_APPLICATION = 'config.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGS_DIR = os.path.join(BASE_DIR, 'logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] [{asctime}] [{module}] [{pathname}] [{lineno}] >> {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] >> {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': None,  # Config later
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': None,  # Config later
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': None,  # Config later
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,  # Keep 5 backup/old-log files
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': None,  # Config later
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'file'],
            'level': None,  # Config later
            'propagate': False,
        },
        'apps.authentication': {
            'handlers': ['console', 'file'],
            'level': None,  # Config later
            'propagate': False,
        },
        'apps.quiz': {
            'handlers': ['console', 'file'],
            'level': None,  # Config later
            'propagate': False,
        },
    }
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}
