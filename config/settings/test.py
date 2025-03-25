from .base import *
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

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

SIMPLE_JWT['SIGNING_KEY'] = SECRET_KEY

# Disable security features that might slow down tests
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

LOGGING['handlers']['console']['level'] = 'WARNING'
LOGGING['handlers'].pop('file', None)

for logger in LOGGING['loggers'].values():
    logger['handlers'] = ['console']
    logger['level'] = 'WARNING'

class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
