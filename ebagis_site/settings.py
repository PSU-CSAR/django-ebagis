"""
Django settings for ebagis project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from __future__ import absolute_import
from ebagis import setup as ebagis_setup
from . import secret

try:
    from . import email
except ImportError:
    raise Exception(
        "Please copy ebagis_site/email_template.py to " +
        "ebagis_site/email.py and edit the values as required."
    )


# this is a really stupid hack for arc 10.3
try:
    # needed this next line for a weird RuntimeError saying NotInitialized
    import arcserver
    import arcpy
    arcpy.Exists(r"..\arcpy_hack\test_img.tif")
except Exception as e:
    print e
    print "Error in initiallizing arcpy for django."


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secret.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.sites',

    'django_extensions',
    'django_windows_tools',
    'djcelery',

    #'debug_toolbar',

    #project
    'ebagis',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'account.middleware.LocaleMiddleware',
    'account.middleware.TimezoneMiddleware',
)

ROOT_URLCONF = 'ebagis_site.urls'
WSGI_APPLICATION = 'ebagis_site.wsgi.application'

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = secret.DATABASE_SETTINGS

# Email
EMAIL_HOST = email.HOST
EMAIL_PORT = email.PORT
EMAIL_HOST_USER = email.USER
EMAIL_HOST_PASSWORD = email.PASSWORD
EMAIL_SUBJECT_PREFIX = email.SUBJECT_PREFIX
EMAIL_USE_SSL = email.USE_SSL
DEFAULT_FROM_EMAIL = email.USER


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'US/Pacific'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# celery settings
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYD_CONCURRENCY = 4


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

SITE_STATIC_ROOT = os.path.join(BASE_DIR, 'local_static')
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.static',
)


# AOI storage/temp unzip location
EBAGIS_AOI_DIRECTORY = os.path.join(BASE_DIR, 'AOIs')
EBAGIS_UPLOADS_DIRECTORY = os.path.join(MEDIA_ROOT, "uploads" + "/%Y/%m/%d")

# call the setup function to add relevant settings
ebagis_setup(__name__)


# authentication settings
AUTHENTICATION_BACKENDS = (
    # basic django auth backend
    'django.contrib.auth.backends.ModelBackend',
)

# cache settings
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


## URL PATH SETTINGS
# TODO: move into urls.py?
# settings for UI
UI_ROOT = r"^ui/"

# settings for rest framework
REST_ROOT = r"^api/rest/"


# settings for graphing data model
GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}


# logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'formatter': 'verbose',
            #'maxBytes': 1024 * 1024 * 5,  # 5 mb
        },
        'celery': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'celery.log'),
            'formatter': 'simple',
            #'maxBytes': 1024 * 1024 * 5,  # 5 mb
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['celery'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'ebagis': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'drf_chunked_upload': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}

# django sites
SITE_ID = 1
