"""
Django settings for ebagis project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from __future__ import absolute_import


#email settings from external file
try:
    from .email import *
except ImportError:
    raise Exception(
        "Please copy ebagis_site/email_template.py to " +
        "ebagis_site/email.py and edit the values as required."
    )


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = (
    # project
    #'test_ui',

    # django libs
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.sites',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Session auth causes problems with token auth logout for some reason
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'ebagis.urls'
WSGI_APPLICATION = 'ebagis.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'US/Pacific'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Django user model
AUTH_USER_MODEL = 'auth.User'


## URL PATH SETTINGS
# settings for rest framework
REST_ROOT = "api/rest/"


STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

SITE_STATIC_ROOT = os.path.join(BASE_DIR, 'local_static')
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
