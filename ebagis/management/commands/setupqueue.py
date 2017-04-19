from __future__ import absolute_import, print_function

import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Configure a Rabbit MQ vhost and user for this project instance.'

    requires_system_checks = False
    can_import_settings = True

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-D',
            '--delete',
            action='store_true',
            help=('Remove the Rabbit MQ vhost and user configuration. '
                  'WARNING: THIS OPERAITON IS IRREVERSABLE. '
                  'ANY DATA IN THE QUEUE MAY BE LOST.'),
        )
        parser.add_argument(
            '--rabbitmqctl-exe',
            default=r'C:\Program Files (x86)\RabbitMQ Server\rabbitmq_server-3.4.4\sbin\rabbitmqctl.bat',
            help=('Path to the rabbitmqctl.exe if it is not on the path. '
                  r'Default uses C:\Program Files (x86)\RabbitMQ Server'
                  r'\rabbitmq_server-3.4.4\sbin\rabbitmqctl.bat'),
        )

    def setup_permission(self, delete=False):
        if not delete:
            cmd = [
                self.rabbitmq,
                'set_permissions',
                '-p',
                settings.INSTANCE_NAME,
                settings.CELERY_BROKER_USER,
                '.*',
                '.*',
                '.*',
                ]
            subprocess.check_call(cmd)

    def setup_user(self, delete=False):
        cmd = [self.rabbitmq, 'add_user',
               settings.CELERY_BROKER_USER, settings.CELERY_BROKER_PASSWORD]
        if delete:
            cmd = [self.rabbitmq, 'delete_user', settings.CELERY_BROKER_USER]
        subprocess.check_call(cmd)

    def setup_vhost(self, delete=False):
        action = 'delete_vhost' if delete else 'add_vhost'
        cmd = [self.rabbitmq, action, settings.INSTANCE_NAME]
        subprocess.check_call(cmd)

    def handle(self, *args, **options):
        self.rabbitmq = options.get('rabbitmqctl_exe')
        delete = options.get('delete')

        self.setup_vhost(delete=delete)
        self.setup_user(delete=delete)
        self.setup_permission(delete=delete)
