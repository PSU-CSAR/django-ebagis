from __future__ import absolute_import

from split_settings.tools import optional, include

from ..management.commands.install import load_conf_file


conf_settings = load_conf_file()

INSTANCE_NAME = conf_settings.get('INSTANCE_NAME')
ENV = conf_settings.get('ENV', 'production')

SECRET_KEY = conf_settings.get('SECRET_KEY')

CELERY_BROKER_USER = conf_settings.get('CELERY_BROKER_USER', INSTANCE_NAME)
CELERY_BROKER_PASSWORD = conf_settings.get('CELERY_BROKER_PASSWORD')

DATABASE_NAME = conf_settings.get('DATABASE_NAME', INSTANCE_NAME)
DATABASE_USER = conf_settings.get('DATABASE_USER', INSTANCE_NAME)
DATABASE_PASSWORD = conf_settings.get('DATABASE_PASSWORD')
DATABASE_HOST = conf_settings.get('DATABASE_HOST', None)
DATABASE_PORT = conf_settings.get('DATABASE_PORT', None)

SITE_DOMAIN_NAME = conf_settings.get('SITE_DOMAIN_NAME', None)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = conf_settings.get('DEBUG', False)


# first pull in the base settings
settings_files = [
    'base.py',
    'auth.py',
    'caching.py',
    'celery.py',
    'database.py',
    'ebagis.py',
    'logging.py',
    'templates.py',
    'rest.py',
]

# add the env-specific settings and any additional settings
settings_files.append(optional(ENV+'.py'))
settings_files.extend(conf_settings.get('ADDITIONAL_SETTING_FILES', []))

# always use the local settings file if present
settings_files.append(optional('local_settings.py'))

# now load all the settings files
include(*settings_files, scope=globals())
