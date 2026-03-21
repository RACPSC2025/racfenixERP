from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Allauth config obligatoria para producción (recomendada incluso en desarrollo)
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'