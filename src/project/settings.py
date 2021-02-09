"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import json
from urllib.parse import urlparse

from envparse import env


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
VAR_DIR = os.path.join(PROJECT_ROOT, 'var')
CERTIFICATES_DIR = os.path.join(VAR_DIR, 'certificates')
BUILD = env.bool('DJANGO_BUILD', default=False)

env.read_envfile(os.path.join(PROJECT_ROOT, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('DJANGO_SECRET_KEY', default='DUMMY_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', default=True)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['*'])

VERSION = env.str('VERSION', default=None)
BUILD_TIME = env.str('BUILD_TIME', default=None)
COMMIT = env.str('COMMIT', default=None)
SENTRY_DSN = os.environ.get('SENTRY_DSN')

SENTRY_CONFIG = {
    'dsn': SENTRY_DSN,
    'release': os.environ.get('DEPLOY_UUID'),
}

SITE_ID = 1
TIME_ZONE = 'Europe/Moscow'

CELERY_RESULT_BACKEND = 'redis://redis/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 172800}
CELERY_BROKER_URL = os.environ.get('BROKER_URL') or 'redis://redis/0'

CELERY_SEND_TASK_ERROR_EMAILS = False

CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'

CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = TIME_ZONE


if SENTRY_DSN:
    url_obj = urlparse(SENTRY_DSN)
    if all([url_obj.scheme, url_obj.hostname, url_obj.path, url_obj.username]):
        CSP_REPORT_URI = "{}://{}/api{}/security/?sentry_key={}".format(
            url_obj.scheme,
            url_obj.hostname,
            url_obj.path,
            url_obj.username
        )

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'ifns',
    'django_celery_results',
    'djnewsletter',
    'project.apps.ProjectConfig',
    'django_prometheus',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

EMAIL_BACKEND = 'djnewsletter.backends.EmailBackend'

DJNEWSLETTER_UNISENDER_URL = os.environ.get('DJNEWSLETTER_UNISENDER_URL') or 'https://eu1.unione.io'

ROOT_URLCONF = 'project.urls'

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

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
if BUILD:
    DATABASES = {}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_NAME', 'ifns'),
            'USER': os.environ.get('POSTGRES_USER', 'ifns'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'ifns'),
            'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
            'PORT': 5432,
        }
    }


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/


LANGUAGE_CODE = 'ru-RU'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

try:
    from .local_settings import *
except ImportError:
    pass

from .conf.logger import *
