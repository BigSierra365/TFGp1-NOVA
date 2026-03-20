# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from dotenv import load_dotenv
import django.contrib.auth
from pathlib import Path
from django.utils.translation import gettext_lazy as _

"""
Configuración de Django para el proyecto core.

Configuración generada con 'django-admin startproject' usando Django 5.2.3.

Para más información sobre este archivo, consulta:
https://docs.djangoproject.com/en/5.2/topics/settings/

Para ver la lista completa de configuraciones y sus valores, consulta:
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# ==================================================
# Configuración de rutas base
# ==================================================
# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================================================
# Configuración de seguridad
# ==================================================
# Clave secreta usada en producción (¡mantener en secreto!)
SECRET_KEY = os.getenv('SECRET_KEY', '')
# Modo depuración: desactivar en producción
DEBUG = True
# Hosts permitidos
ALLOWED_HOSTS = []

# ==================================================
# Aplicaciones instaladas
# ==================================================
INSTALLED_APPS = [
    # Aplicaciones por defecto de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Aplicaciones de terceros
    'rest_framework',
    'corsheaders',
    # Aplicaciones locales
    'app',
]

# ==================================================
# Middleware
# ==================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==================================================
# Configuración de URLs
# ==================================================
ROOT_URLCONF = 'core.urls'

# ==================================================
# Configuración de plantillas
# ==================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Directorio global de plantillas
        'APP_DIRS': True,  # Buscar plantillas en los directorios de las aplicaciones
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

# ==================================================
# Configuración WSGI
# ==================================================
WSGI_APPLICATION = 'core.wsgi.application'

# ==================================================
# Configuración de la base de datos
# ==================================================
if DEBUG == False:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
if DEBUG == True:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'nova',
            'USER': 'tfgadmin',
            'PASSWORD': 'tfgadmin',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

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

# Internationalization
LANGUAGE_CODE = 'es'  # Default language
TIME_ZONE = 'Europe/Madrid'
USE_I18N = False
USE_L10N = False
USE_TZ = True

# Format localization
FORMAT_MODULE_PATH = [
    'core.formats',
]

# Site settings
SITE_ID = 1
SITE_NAME = "NOVA"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'djblets.siteconfig.context_processors.siteconfig',
    'djblets.util.context_processors.settingsVars',
    'djblets.util.context_processors.siteRoot',
    'djblets.util.context_processors.ajaxSerial',
    'djblets.util.context_processors.mediaSerial',
    'django.template.context_processors.request',
    'app.context_processors.cart_counter',
)

# Archivos estáticos
STATIC_URL = '/static/'    #js, css3, ..
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'  #videos, imágenes
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Directorios de archivos estáticos
STATICFILES_DIRS = (
    ('css', os.path.join(STATIC_ROOT, 'css')),
    ('js', os.path.join(STATIC_ROOT, 'js')),
    ('img', os.path.join(STATIC_ROOT, 'img')),
)

# Buscadores de archivos estáticos
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Cargadores de plantillas
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# Directorios de plantillas
TEMPLATE_DIRS = (
)
# Configuración de correo electrónico

# Para desarrollo y pruebas (los correos se muestran en la consola)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Para producción con Gmail (descomentar y configurar cuando estés listo)
'''
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '3lp3p3elpepe@gmail.com'  # Cambiar por tu dirección de correo

# GENERAR UNA NUEVA CONTRASEÑA DE APLICACIÓN:
# 1. Ve a https://myaccount.google.com/security
# 2. Activa la verificación en dos pasos si no está activada
# 3. Luego ve a 'Contraseñas de aplicación'
# 4. Selecciona 'Otra' y nombra la app 'Django App'
# 5. Copia la contraseña generada y ponla abajo sin espacios
EMAIL_HOST_PASSWORD = ''  # Poner la nueva contraseña de aplicación aquí
'''

# Configuración adicional para correo
DEFAULT_FROM_EMAIL = 'NOVA Store <no-reply@novastore.com>'  # Nombre mostrado en los correos
SERVER_EMAIL = 'no-reply@novastore.com'  # Para correos de error

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'profile'
LOGOUT_REDIRECT_URL = 'login'

# Stripe
# Claves de prueba de Stripe (no son claves reales, son para pruebas)
# IMPORTANTE: Debes reemplazar estas claves con tus propias claves de prueba de Stripe
# Puedes obtenerlas en: https://dashboard.stripe.com/test/apikeys
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "") # Tu clave publicable (comienza con pk_test_...)
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")     # Tu clave secreta (comienza con sk_test_...)