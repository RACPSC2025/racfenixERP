from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-y8y9o@-l+b#lim8if$6$y9!v^-+z+#dr)%i@*hcws6iefex0jw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
BASE_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.inlines',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

LOCAL_APPS=[
    'core',
    'apps.products',
    'apps.users',
]

THIRD_APPS=[
    'rest_framework',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'simple_history',
    'django_htmx',
    'tailwind',
]

INSTALLED_APPS = BASE_APPS + THIRD_APPS + LOCAL_APPS 

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'django_htmx.middleware.HtmxMiddleware',

]

ROOT_URLCONF = 'core.urls'

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
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Backend Auths (Django intenta el primero, si falla va al segundo)
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # Login normal por Admin
    'allauth.account.auth_backends.AuthenticationBackend', # Login por Allauth
)

# allauth config mínima para custom user sin username
ACCOUNT_USERMODEL_USERNAME_FIELD = None
# Solo pedimos email en el signup,  obligatorio con el asterisco *
ACCOUNT_SIGNUP_FIELDS = ['email*'] 
ACCOUNT_LOGIN_METHODS = {'email'}
AUTH_USER_MODEL = 'users.User'

ACCOUNT_FORMS = {
    "signup": "users.forms.CustomSignupForm",
}


# Configuración de Unfold
# config/settings.py

# config/settings.py

UNFOLD = {
    "SITE_TITLE": "ERP Fenix Soft",
    "SITE_HEADER": "Dashboard",
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    # "THEME": "dark",
    
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Users",
                "collapsible": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": "/admin/users/user/",
                        "permission": lambda request: request.user.has_perm("users.view_user"),
                    },
                ],
            },
            {
                "title": "Social Accounts",
                "collapsible": True,
                "collapse": True,
                "items": [
                    {
                        "title": "Social accounts",
                        "icon": "share",
                        "link": "/admin/socialaccount/socialaccount/",
                        "permission": lambda request: request.user.has_perm("socialaccount.view_socialaccount"),
                    },
                    {
                        "title": "Social applications",
                        "icon": "api",
                        "link": "/admin/socialaccount/socialapp/",
                        "permission": lambda request: request.user.has_perm("socialaccount.view_socialapp"),
                    },
                    {
                        "title": "Social application tokens",
                        "icon": "vpn_key",
                        "link": "/admin/socialaccount/socialtoken/",
                        "permission": lambda request: request.user.has_perm("socialaccount.view_socialtoken"),
                    },
                ],
            },
            {
                "title": "Authentication and Authorization",
                "collapsible": True,
                "items": [
                    {
                        "title": "Groups",
                        "icon": "group",
                        "link": "/admin/auth/group/",
                        "permission": lambda request: request.user.has_perm("auth.view_group"),
                    },
                ],
            },
        ],
    },
    
    # Evitar errores de traducción
    "TITLES": {
        "login": "login",
        "logout": "logout",
    },
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'