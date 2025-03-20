from .base import *
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = []  # Keeping this empty will take this by default: ['localhost', '127.0.0.1']

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

os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['handlers']['file']['level'] = 'DEBUG'
LOGGING['handlers']['file']['filename'] = os.path.join(LOGS_DIR, 'dev.log')

for logger in LOGGING['loggers'].values():
    logger['level'] = 'DEBUG'

LOGGING['loggers']['django']['level'] = 'WARNING'
