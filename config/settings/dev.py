from .base import *
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file

DEBUG = True

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

os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['handlers']['file']['level'] = 'DEBUG'
LOGGING['handlers']['file']['filename'] = os.path.join(LOGS_DIR, 'dev.log')

for logger in LOGGING['loggers'].values():
    logger['level'] = 'DEBUG'

LOGGING['loggers']['django']['level'] = 'WARNING'
