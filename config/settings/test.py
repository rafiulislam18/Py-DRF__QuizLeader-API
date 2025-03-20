from .base import *
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # In-memory database for faster tests
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
