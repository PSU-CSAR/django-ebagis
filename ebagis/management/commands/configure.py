from __future__ import absolute_import

import os
import random
import string
import yaml

from getpass import getpass

from django.core.management.base import BaseCommand, CommandError

import ebagis.settings


def generate_secret_key(length=50):
    choices = '{}{}{}'.format(
        string.ascii_letters,
        string.digits,
        string.punctuation.replace('\'', '').replace('\\', ''),
    )
    return ''.join(
        [random.SystemRandom().choice(choices) for i in range(length)]
    )


def destruct_path(path):
    '''take a path and break it's pieces into a list:
    d:\projects\ebagis\development becomes
    ['d:', 'projects', 'ebagis', 'development']'''

    folders = []
    while True:
        path, folder = os.path.split(path)

        if folder != "":
            folders.append(folder)
        else:
            if path != "":
                folders.append(path)

            break

    return folders[::-1]


def get_project_root(*args):
    # path should look something like
    # d:\development\ebagis_dev\django-ebagis\ebagis\settings\__init__.pyc
    # which should be split into separate elements in a list
    # the project root is 4th from the end, which we use to slice and
    # reconstruct into d:\development\ebagis_dev\django-ebagis
    args = destruct_path(ebagis.settings.__file__)[:-4].extend(args)
    return os.path.join(*args)


def get_instance_name():
    try:
        # path should look something like
        # d:\development\ebagis_dev\django-ebagis\ebagis\settings\__init__.pyc
        # which should be split into separate elements in a list
        # the instance name is 5th from the end (ebagis_dev)
        return destruct_path(ebagis.settings.__file__)[-5]
    except IndexError:
        # path was too short and we couldn't get anything from it
        return None


def get_env_name():
    try:
        # path should look something like
        # d:\development\ebagis_dev\django-ebagis\ebagis\settings\__init__.pyc
        # which should be split into separate elements in a list
        # the instance name is 6th from the end (development)
        return destruct_path(ebagis.settings.__file__)[-6]
    except IndexError:
        # path was too short and we couldn't get anything from it
        return None


def get_settings_file(file_name=None):
    if file_name:
        return os.path.join(
            get_project_root(),
            'secret.py'
        )
    return ebagis.settings.__file__


def default_output_file():
    return get_project_root('project_settings.yml')


class Command(BaseCommand):
    help = """Create the configuration settings for this ebagis instance."""

    can_import_settings = False
    leave_locale_alone = True

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-n',
            '--instance-name',
            help='The name of the ebagis instance. Default the name of the directory containing this django-ebagis instance.',
        )
        parser.add_argument(
            '-N',
            '--db-name',
            help='The name of the database. Default is the instance name.',
        )
        parser.add_argument(
            '-u',
            '--db-user',
            help='The name of the DB user. Default is the instance name.',
        )
        parser.add_argument(
            '-p',
            '--db-password',
            help='Password for the specified DB user. Default is to prompt user for input.',
        )
        parser.add_argument(
            '--db-host',
            help='Hostname of the DB server. Default is None, which means localhost.',
        )
        parser.add_argument(
            '--db-port',
            help='Port for the DB server. Default is None, which will use postgres default.',
        )
        parser.add_argument(
            '-U',
            '--broker-user',
            help='The name of the message broker user. Default is the instance name.',
        )
        parser.add_argument(
            '-P',
            '--broker-password',
            help='Password for the specified broker user. Default is to prompt user for input.',
        )
        parser.add_argument(
            '-k',
            '--secret-key',
            help='A django-style secret key. Default is to generate a random string of chars.',
        )
        parser.add_argument(
            '-l',
            '--secret-key-length',
            type=int,
            default=50,
            help='The number of chars if generating a secret key. Default is 50 chars.',
        )
        parser.add_argument(
            '-e',
            '--env',
            help='The environment name. Must match an env-specific settings module. Default is to inspect instance path and extract.',
        )
        parser.add_argument(
            '-a',
            '--additional-settings-file',
            action='append',
            help='The name of an addtional settings file to use.',
        )
        parser.add_argument(
            '-o',
            '--output-file',
            help='Where to output settings file. Default is a file named "project_settings.yml" in the instance root.',
        )

    def handle(self, *args, **options):
        settings = {}

        output_file = options.get('output_file', default_output_file()),

        settings['ENV'] = options.get('env', get_env_name())

        if not settings['ENV']:
            raise CommandError(
                'Could not extract env name from path and none specified.'
            )

        if not os.path.isfile(get_settings_file(settings['ENV'])):
            raise Warning(
                'Could not find settings file for env named {}'
                .format(settings['ENV'])
            )

        settings['INSTANCE_NAME'] = options.get(
            'instance_name',
            get_instance_name(),
        )

        if not settings['INSTANCE_NAME']:
            raise CommandError(
                'Could not extract instance name from path and none specified.'
             )

        settings['SECRET_KEY'] = options.get(
            'secret_key',
            generate_secret_key(options.get('secret_key_length'))
        )

        settings['DATABASE_NAME'] = options.get(
            'db_name',
            settings['INSTANCE_NAME'],
        )
        settings['DATABASE_USER'] = options.get(
            'db_user',
            settings['INSTANCE_NAME'],
        )
        settings['DATABASE_PASSWORD'] = options.get(
            'db_password',
            getpass('Please enter the database user password: '),
        )
        settings['DATABASE_HOST'] = options.get('db_host', None)
        settings['DATABASE_PORT'] = options.get('db_port', None)

        settings['BROKER_USER'] = options.get(
            'broker_user',
            settings['INSTANCE_NAME'],
        )
        settings['BROKER_PASSWORD'] = options.get(
            'broker_password',
            getpass('Please enter the broker user password: '),
        )

        with open(output_file, 'w') as outfile:
            yaml.dump(settings, outfile)
