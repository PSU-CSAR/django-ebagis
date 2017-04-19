from __future__ import absolute_import

import os
import sys
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """Configure an IIS site for this project instance."""

    requires_system_checks = False
    can_import_settings = True

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-s',
            '--start',
            action='store_true',
            help=('Start a linked celery task instance if it is not running.'),
        )
        parser.add_argument(
            '-S',
            '--stop',
            action='store_true',
            help=('Stop a linked celery task instance if it is running.'),
        )
        parser.add_argument(
            '-r',
            '--restart',
            action='store_true',
            help=('Restart a linked celery task instance.'),
        )
        parser.add_argument(
            '-D',
            '--delete',
            action='store_true',
            help=('Remove a linked celery task instance. '
                  'WARNING: THIS OPERAITON IS IRREVERSABLE.'),
        )

    def remove_task(self):
        cmd = ['schtasks', '/delete', '/f', '/tn', self.task_name]
        subprocess.call(cmd)

    def start_task(self):
        cmd = ['schtasks', '/run', '/tn', self.task_name]
        subprocess.call(cmd)

    def stop_task(self):
        cmd = ['schtasks', '/end', '/tn', self.task_name]
        subprocess.call(cmd)

    def create_task(self):
        cmd = [
            'schtasks',
            '/create',
            '/tn',
            self.task_name,
            '/tr',
            '{} runcelery --noreload'.format(sys.argv[0]),
            '/sc',
            'onstart',
            '/ru',
            'SYSTEM',
        ]
        subprocess.call(cmd)
        print('WARNING: Windows Task Scheduler provides no command line '
              'access for unsetting the default option to stop a task if '
              'it runs for more than 3 days.')
        print('')
        print('To keep this celery process running indefinitely:')
        print('')
        print('  - open Task Scheduler')
        print('  - find the task named {}'.format(self.task_name))
        print('  - right-click the task and choose properties')
        print('  - go to the "Settings" tab')
        print('  - uncheck "Stop the task if it runs longer than"')
        print('')
        print('Now your celery task should be all set to go.')

    def handle(self, *args, **options):
        self.task_name = settings.INSTANCE_NAME + '_celery'

        if options.get('delete'):
            self.stop_task()
            self.remove_task()
        elif options.get('start'):
            self.start_task()
        elif options.get('stop'):
            self.stop_task()
        elif options.get('restart'):
            self.stop_task()
            self.start_task()
        else:
            self.create_task()
            self.start_task()
