from __future__ import absolute_import, unicode_literals

import os
import sys
from datetime import datetime

from celery import current_app
from celery.bin import worker

from django.conf import settings
from django.core.management.base import BaseCommand

from django.utils import autoreload


class Command(BaseCommand):
    help = ("Starts a celery process listing for tasks "
            "to process from the current project instance.")

    # Validation is called explicitly each time celery is reloaded.
    requires_system_checks = False
    leave_locale_alone = True

    def add_arguments(self, parser):
        parser.add_argument(
            '--noreload',
            action='store_false',
            dest='use_reloader',
            help=('Tells celery to NOT use the auto-reloader. '
                  'Highly recommended in production.'),
        )

    def handle(self, *args, **options):
        """Run celery, using the autoreloader if needed."""
        use_reloader = options['use_reloader']

        if use_reloader:
            if os.path.basename(sys.argv[0]) == 'ebagis':
                sys.argv[0] += '-script.py'
            autoreload.main(self.inner_run, None, options)
        else:
            self.inner_run(None, **options)

    def inner_run(self, *args, **options):
        # If an exception was silenced in ManagementUtility.execute in order
        # to be raised in the child process, raise it now.
        autoreload.raise_last_exception()

        # 'shutdown_message' is a stealth option.
        shutdown_message = options.get('shutdown_message', '')
        quit_command = 'CTRL-BREAK' if sys.platform == 'win32' else 'CONTROL-C'

        self.stdout.write("Performing system checks...\n\n")
        self.check(display_num_errors=True)
        # Need to check migrations here, so can't use the
        # requires_migrations_check attribute.
        self.check_migrations()
        now = datetime.now().strftime('%B %d, %Y - %X')
        self.stdout.write(now)
        self.stdout.write((
            "Django version %(version)s, using settings %(settings)r\n"
            "Starting celery\n"
            "Quit celery with %(quit_command)s.\n"
        ) % {
            "version": self.get_version(),
            "settings": settings.SETTINGS_MODULE,
            "quit_command": quit_command,
        })

        try:
            application = current_app._get_current_object()

            celery_worker = worker.worker(app=application)

            options = {
                'broker': settings.BROKER_URL,
                'loglevel': 'INFO',
                'traceback': True,
                'hostname': settings.INSTANCE_NAME,
            }

            celery_worker.run(**options)
        except KeyboardInterrupt:
            if shutdown_message:
                self.stdout.write(shutdown_message)
            sys.exit(0)
