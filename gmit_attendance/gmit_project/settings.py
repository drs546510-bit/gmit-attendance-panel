"""
Django settings for GMIT Student Attendance Panel.
"""

import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: change this before real deployment!
# On Render, set a real SECRET_KEY as an Environment Variable — this fallback
# value is only used for local development.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-CHANGE-THIS-KEY-BEFORE-DEPLOYMENT-p6a-@-7!x4ue2637r',
)

# Locally this defaults to True. On Render, set the environment variable
# DEBUG = False (as text) once everything is working.
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Locally '*' allows access from any device on your Wi-Fi.
# On Render, RENDER_EXTERNAL_HOSTNAME is set automatically for you, so your
# live *.onrender.com domain is added on its own — no manual edit needed.
ALLOWED_HOSTS = ['*'] if DEBUG else []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS = [f'https://{RENDER_EXTERNAL_HOSTNAME}']

# On Railway (or any other host), set an environment variable called
# DJANGO_ALLOWED_HOSTS with your live domain, e.g.:
#   DJANGO_ALLOWED_HOSTS = gmit-attendance-panel-production.up.railway.app
# You can list more than one, separated by commas.
EXTRA_ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
if EXTRA_ALLOWED_HOSTS:
    hosts = [h.strip() for h in EXTRA_ALLOWED_HOSTS.split(',') if h.strip()]
    ALLOWED_HOSTS += hosts
    CSRF_TRUSTED_ORIGINS = [f'https://{h}' for h in hosts]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'attendance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serves CSS/JS on Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gmit_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'gmit_project.wsgi.application'

# ---------------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------------
# Local development (your PC): MySQL via XAMPP / MySQL Workbench, as before.
# On Render: Render automatically provides a DATABASE_URL environment
# variable once you attach a Postgres database to this web service — when
# that variable exists, it's used automatically instead of MySQL. You don't
# need to change any code, just add the database on Render's dashboard.
#
# To quickly test locally WITHOUT installing MySQL, set USE_SQLITE = True
# as an environment variable.
# ---------------------------------------------------------------------------

DATABASE_URL = os.environ.get('DATABASE_URL')
USE_SQLITE = os.environ.get('USE_SQLITE', 'False') == 'True'

if DATABASE_URL:
    # Running on Render (or anywhere DATABASE_URL is provided) — use Postgres.
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
    }
elif USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'gmit_attendance_db'),
            'USER': os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'root123'),
            'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

# Custom user model (adds `role`: ADMIN / TEACHER / STUDENT)
AUTH_USER_MODEL = 'attendance.CustomUser'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login / logout redirects
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard_redirect'
LOGOUT_REDIRECT_URL = 'login'

# Extra security settings that only matter once this is live on Render
# (DEBUG=False). They don't affect anything while you're developing locally.
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


