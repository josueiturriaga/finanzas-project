from pathlib import Path
import os
from dotenv import load_dotenv  # <--- IMPORTANTE: Importamos la librería

# Cargar las variables del archivo .env
load_dotenv()  # <--- IMPORTANTE: Esto lee tu archivo secreto

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# AHORA LA CLAVE VIENE DEL ARCHIVO OCULTO, YA NO ESTÁ VISIBLE
SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'finanzas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'finanzas_project.urls'

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

WSGI_APPLICATION = 'finanzas_project.wsgi.application'


if 'PYTHONANYWHERE_DOMAIN' in os.environ:
    # --- CONFIGURACIÓN PARA LA NUBE ---
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'josuefinanzas$finanzas_db',
            'USER': 'josuefinanzas',
            # AQUI USAMOS LA CLAVE OCULTA DEL .ENV
            'PASSWORD': os.getenv('DB_PASSWORD_NUBE'),
            'HOST': 'josuefinanzas.mysql.pythonanywhere-services.com',
        }
    }
else:
    # --- CONFIGURACIÓN PARA TU PC (SQLyog) ---
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'finanzas_db',
            'USER': 'root',
            'PASSWORD': '',  # En local suele ser vacía, así que esto está bien
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- CONFIGURACIÓN DE LOGIN ---
LOGIN_REDIRECT_URL = 'menu'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# --- CONFIGURACIÓN DE CORREO (Consola) ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'