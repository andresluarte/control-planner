"""
Django settings for construccion1 project.
"""

from pathlib import Path
import os 
import dj_database_url
DEBUG = True
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-+bfs32#558dz+8^9@pjjc78j@t(c9ug@r6cnzx5qn%ab5^5*7@')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Hosts permitidos
ALLOWED_HOSTS = ['.herokuapp.com', 'localhost', '127.0.0.1']

# Configuración de login
LOGIN_REDIRECT_URL = '/mis-proyectos/'  
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/logout/'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'construccion1app.apps.Construccion1AppConfig', 
    'webpush',
    'pwa',
]

# Configuración de WebPush
WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": "BN8Mo7Z1c2CBELfxGgDE0jq77ZQmsF5fBPYoNtUv1ETI23MJsUx-fqTghB_CoYbMvODzrzl2DYm9832ADljoKOU==",
    "VAPID_PRIVATE_KEY": "rui2WBK3SzmAEA7FmJXf3FdtgjM4Vno2XOCV87xaRHI",
    "VAPID_ADMIN_EMAIL": "andres.luarte@luartech.cl"
}

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuración de zona horaria
TIME_ZONE = 'America/Santiago'
USE_TZ = True

ROOT_URLCONF = 'construccion1.urls'

# Templates
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
                'construccion1app.context_processors.notificaciones_context',
                'construccion1app.context_processors.webpush_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'construccion1.wsgi.application'

# Database configuration
if 'DATABASE_URL' in os.environ:
    # Configuración para Heroku (producción)
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True
        )
    }
else:
    # Configuración para desarrollo local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'construccion1bd',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

# Custom user model
AUTH_USER_MODEL = 'construccion1app.Usuario'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-es'
USE_I18N = True


CSRF_TRUSTED_ORIGINS = [
    'https://control-plannner-4c7ab22173ea.herokuapp.com',
    'https://*.herokuapp.com',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Progressive Web App (PWA)
PWA_APP_NAME = 'ConstruApp'
PWA_APP_DESCRIPTION = "Control Planner para obras"
PWA_APP_THEME_COLOR = '#0a1f44'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'portrait'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_ICONS = [
    {'src': '/static/construccion1app/img/logo2.jpeg', 'sizes': '512x512'}
]
PWA_APP_ICONS_APPLE = [
    {'src': '/static/construccion1app/img/logo2.jpeg', 'sizes': '512x512'}
]
PWA_APP_SPLASH_SCREEN = [
    {'src': '/static/construccion1app/img/logo2.jpeg', 'media': '(prefers-color-scheme: light)'}
]
PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'es-ES'