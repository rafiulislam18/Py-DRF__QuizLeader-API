from .base import *


DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING['handlers']['console']['level'] = 'INFO'
LOGGING['handlers']['file']['level'] = 'INFO'
LOGGING['handlers']['file']['filename'] = os.path.join(LOGS_DIR, 'prod.log')

for logger in LOGGING['loggers'].values():
    logger['level'] = 'WARNING'

LOGGING['loggers']['django']['level'] = 'ERROR'
