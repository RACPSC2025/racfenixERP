from .base import *

# ===========================================
# SETTINGS PARA DESARROLLO LOCAL
# ===========================================

# -------------------------------------------
# Database (SQLite para desarrollo)
# -------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': BASE_DIR / env('DB_NAME', default='db.sqlite3'),
        # Si usas PostgreSQL en desarrollo, descomenta:
        # 'USER': env('DB_USER', default=''),
        # 'PASSWORD': env('DB_PASSWORD', default=''),
        # 'HOST': env('DB_HOST', default='localhost'),
        # 'PORT': env('DB_PORT', default='5432'),
    }
}

# -------------------------------------------
# Email (Consola para desarrollo)
# -------------------------------------------
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)

# -------------------------------------------
# CSRF & Session (Desarrollo)
# -------------------------------------------
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['http://localhost:8000'])
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False