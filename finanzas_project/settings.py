from pathlib import Path
import os  # <--- IMPORTANTE: Necesario para la configuración de la nube

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-12&w3f+zqii4orv*8@ks^a7m5g7ma7w6&)km3)flq$hcde+l)^'

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
            'PASSWORD': 'josue1234',  # <--- AQUI PONES LA QUE CREASTE EN EL PASO 1
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
            'PASSWORD': '',  # En tu PC suele ser vacía
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

LANGUAGE_CODE = 'es-es'       # <--- Ajustado a Español

TIME_ZONE = 'America/Santiago' # <--- Ajustado a Chile para que las fechas sean correctas

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
# Esta línea es VITAL para que funcionen los estilos en la nube
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- CONFIGURACIÓN DE LOGIN ---
LOGIN_REDIRECT_URL = 'menu'   # Cuando entras, te lleva al menú
LOGOUT_REDIRECT_URL = 'login' # Cuando sales, te lleva al login
LOGIN_URL = 'login'           # Si no estás logueado, te manda aquí

# --- NUEVO: CORREO POR CONSOLA ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'