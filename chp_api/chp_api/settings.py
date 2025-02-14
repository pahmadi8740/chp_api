"""
Base Django settings for chp_api project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import os
import environ as environ # type: ignore

from importlib import import_module


# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(env("DEBUG", default=0))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_UPLOAD_MAX_MEMORY_SIZE = None
REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        #'rest_framework_simplejwt.authentication.JWTAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        )
}

AUTHENTICATION_BACKENDS = [
    'oauth2_provider.backends.OAuth2Backend',
    # Uncomment following if you want to access the admin
    'django.contrib.auth.backends.ModelBackend',
]

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope', 'groups': 'Access to your groups'}
}

# Cors stuff (must go before installed apps)
CORS_ALLOWED_ORIGINS = [
        'http://localhost',
        'http://localhost:3000',
        ]

# Application definition
INSTALLED_BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'dispatcher.apps.DispatcherConfig',
    'django_extensions',
    'users',
    'oauth2_provider',
    #'gennifer', # Need to make into CHP app
]

INSTALLED_CHP_APPS = [
    'gene_specificity',
    'gennifer',
    ]

# CHP Versions
VERSIONS = {app_name: app.__version__ for app_name, app in [(app_name, import_module(app_name)) for app_name in INSTALLED_CHP_APPS]}

# Sets up installed apps relevent to django 
INSTALLED_APPS = INSTALLED_BASE_APPS + INSTALLED_CHP_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
]

ROOT_URLCONF = 'chp_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

WSGI_APPLICATION = 'chp_api.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

# Authorization
AUTH_USER_MODEL='users.User'
LOGIN_URL='/admin/login/'

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Hosts Configuration
#ROOT_HOSTCONF = 'chp_api.hosts'

DB_PASSWORD = env("POSTGRES_PASSWORD", default=None)

if not DB_PASSWORD:
    with open(env("POSTGRES_PASSWORD_FILE"), 'r') as db_pwd:
        DB_PASSWORD = db_pwd.readline().strip()

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": DB_PASSWORD,
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    }
}


ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", default=None)
if not ALLOWED_HOSTS:
    with open(env("DJANGO_ALLOWED_HOSTS_FILE"), 'r') as ah_file:
        ALLOWED_HOSTS = ah_file.readline().strip().split(" ")
else:
    ALLOWED_HOSTS = ALLOWED_HOSTS.split(',')

# SECURITY WARNING: keep the secret key used in production secret!
 # Read the secret key from file
SECRET_KEY = env("SECRET_KEY", default=None)
if not SECRET_KEY:
    with open(env("SECRET_KEY_FILE"), 'r') as sk_file:
        SECRET_KEY = sk_file.readline().strip()

CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS", default=None)
if not CSRF_TRUSTED_ORIGINS:
    with open(env("CSRF_TRUSTED_ORIGINS_FILE"), 'r') as csrf_file:
        CSRF_TRUSTED_ORIGINS = csrf_file.readline().strip().split(" ")
else:
    CSRF_TRUSTED_ORIGINS = CSRF_TRUSTED_ORIGINS.split(',')

# Set UN, Email and Password for superuser
DJANGO_SUPERUSER_USERNAME = env("DJANGO_SUPERUSER_USERNAME", default=None)
if not DJANGO_SUPERUSER_USERNAME:
    with open(env("DJANGO_SUPERUSER_USERNAME_FILE"), 'r') as dsu_file:
        os.environ["DJANGO_SUPERUSER_USERNAME"] = dsu_file.readline().strip()

DJANGO_SUPERUSER_EMAIL = env("DJANGO_SUPERUSER_EMAIL", default=None)
if not DJANGO_SUPERUSER_EMAIL:
    with open(env("DJANGO_SUPERUSER_EMAIL_FILE"), 'r') as dse_file:
        os.environ["DJANGO_SUPERUSER_EMAIL"] = dse_file.readline().strip()

DJANGO_SUPERUSER_PASSWORD = env("DJANGO_SUPERUSER_PASSWORD", default=None)
if not DJANGO_SUPERUSER_PASSWORD:
    with open(env("DJANGO_SUPERUSER_PASSWORD_FILE"), 'r') as dsp_file:
        os.environ["DJANGO_SUPERUSER_PASSWORD"] = dsp_file.readline().strip()

# Simple JWT Settings
SIMPLE_JWT = {
        "TOKEN_OBTAIN_SERIALIZER": "chp_api.serializers.ChpTokenObtainPairSerializer",
        }

# Celery Settings
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

# Gennifer settings
GENNIFER_ALGORITHM_URLS = [
        "http://pidc:5000",
        "http://grisli:5000",
        "http://genie3:5000",
        "http://grnboost2:5000",
        "http://bkb-grn:5000",
        ]
