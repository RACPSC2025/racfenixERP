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

# Allauth config mínima opcional para desarrollo (recomendada)
ACCOUNT_EMAIL_VERIFICATION = 'optional'

# Para desarrollo, muestra emails en consola en lugar de enviarlos realmente
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' 

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'