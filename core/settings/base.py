import environ
from pathlib import Path
from django.templatetags.static import static

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializar django-environ
env = environ.Env()
# Leer archivo .env según el entorno (local/production)
environ.Env.read_env(BASE_DIR.parent / '.env.local')

# -------------------------------------------
# Django Core - Variables de Entorno
# -------------------------------------------
SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# ------------------------------------------
# Application definition
# ------------------------------------------
BASE_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.inlines',
    'crispy_forms',
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
    'apps.users',
    'apps.products',
    'apps.purchases',
    'apps.sales',
    'apps.customers',
]

THIRD_APPS=[
    'rest_framework',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'simple_history',
    'django_htmx',
]

INSTALLED_APPS = BASE_APPS + THIRD_APPS + LOCAL_APPS 

# ------------------------------------------
# Middleware
# ------------------------------------------
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

# ------------------------------------------
# Templates
# ------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR.parent / 'templates',
        ],
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

# ------------------------------------------
# Password validation
# ------------------------------------------
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

# -----------------------------------------------------------------------------
# UNFOLD ADMIN CONFIGURATION
# -----------------------------------------------------------------------------
UNFOLD = {
    "SITE_TITLE": "ERP Fenix Soft",
    "SITE_HEADER": "Dashboard",
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    # "THEME": "dark",

    # Aquí es donde Unfold detecta y carga el CSS compilado por tu comando npm
    "STYLES": [
        lambda request: static("css/styles.css"),
    ],

    "DASHBOARD_URL": "/admin/",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Principal",
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": "/admin/",
                        "permission": lambda request: request.user.is_staff,
                    },
                    {
                        "title": "Historial",
                        "icon": "history",
                        "link": "/admin/admin/logentry/",
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
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
                    {
                        "title": "Roles",
                        "icon": "group",
                        "link": "/admin/auth/group/",
                        "permission": lambda request: request.user.has_perm("auth.view_group"),
                    },
                ],
            },
            {
                "title": "Products",
                "collapsible": True,
                "items": [
                    {
                        "title": "Products",
                        "icon": "inventory_2",
                        "link": "/admin/products/product/",
                        "permission": lambda request: request.user.has_perm("products.view_product"),
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": "/admin/products/category/",
                        "permission": lambda request: request.user.has_perm("products.view_category"),
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
        ],
    },
    
    # Evitar errores de traducción
    "TITLES": {
        "login": "login",
        "logout": "logout",
    },
}

CRISPY_ALLOWED_TEMPLATE_PACKS = ["unfold_crispy"]
CRISPY_TEMPLATE_PACK = "unfold_crispy"


# -----------------------------------------------------------------------------
# ALLAUTH CONFIGURATION
# -----------------------------------------------------------------------------

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_SIGNUP_FIELDS = ['email*']
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_VERIFICATION = env('ACCOUNT_EMAIL_VERIFICATION', default='none')
AUTH_USER_MODEL = 'users.User'

# Backend Auths (Django intenta el primero, si falla va al segundo)
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # Login normal por Admin
    'allauth.account.auth_backends.AuthenticationBackend', # Login por Allauth
)

# allauth config mínima para custom user sin username
ACCOUNT_FORMS = {
    "signup": "users.forms.CustomSignupForm",
}

# -----------------------------------------------------------------------------
# INTERNATIONALIZATION
# -----------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Site Framework
SITE_ID = env.int('SITE_ID', default=1)
SITE_NAME = env('SITE_NAME', default='ERP Fenix Soft')
SITE_DOMAIN = env('SITE_DOMAIN', default='http://localhost:8000')


# ------------------------------------------
# Static files (CSS, JavaScript, Images)
# ------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR.parent / 'statics',
]