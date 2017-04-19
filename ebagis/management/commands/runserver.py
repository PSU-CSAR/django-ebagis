import os
import sys

from django.contrib.staticfiles.management.commands.runserver import \
    Command as RunserverCommand


class Command(RunserverCommand):
    def handler(self, *args, **options):
        '''We need to fix the path to the process if calling
        using the ebagis command, so we override runserver'''
        if os.path.basename(sys.argv[0]) == 'ebagis':
            sys.argv[0] += '_script.py'
