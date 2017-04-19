from __future__ import absolute_import

import os
import subprocess

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand
from django.contrib.staticfiles.management.commands import collectstatic

from django_windows_tools.management.commands import winfcgi_install

from ..utils import get_project_root

from . import celerytask

MAX_CONTENT_LENGTH = 2*30
TOUCH_FILE = os.path.join(get_project_root,
                          'touch_this_file_to_update_cgi.txt')

CONFIG_FILE_NAME = 'web.config'

STATIC_CONFIG = os.path.join(settings.STATIC_ROOT, CONFIG_FILE_NAME)
STATIC_CONFIG_STRING = \
'''<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <!-- this configuration overrides the FastCGI handler to let IIS serve the static files -->
    <handlers>
    <clear/>
      <add name="StaticFile" path="*" verb="*" modules="StaticFileModule" resourceType="File" requireAccess="Read" />
    </handlers>
  </system.webServer>
</configuration>
'''

WEB_CONFIG = os.path.join(get_project_root, CONFIG_FILE_NAME)
WEB_CONFIG_STRING = \
'''    <rewrite>
      <rules>
        <rule name="HTTP to HTTPS Redirect" enabled="true" stopProcessing="true">
        <match url="(.*)" />
        <conditions logicalGrouping="MatchAny">
          <add input="{SERVER_PORT_SECURE}" pattern="^0$" />
          </conditions>
          <action type="Redirect" url="https://{HTTP_HOST}{REQUEST_URI}" redirectType="Permanent" />
        </rule>
      </rules>
    </rewrite>'''


class Command(BaseCommand):
    help = """Configure an IIS site for this project instance."""

    requires_system_checks = False
    can_import_settings = True

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-D',
            '--delete',
            action='store_true',
            help=('Remove the linked IIS site. '
                  'WARNING: THIS OPERAITON IS IRREVERSABLE.'),
        )

    def setup_static_assets(self, delete=False):
        if delete:
            os.remove(STATIC_CONFIG)
            return

        # get the static assets to setup proj and create static dir
        management.call_command(collectstatic.Command())
        # place the IIS conf file in the static dir
        with open(STATIC_CONFIG, 'w') as f:
            f.write(STATIC_CONFIG_STRING)

    def create_touch_file(self, delete=False):
        if delete:
            os.remove(TOUCH_FILE)
            return

        with open(TOUCH_FILE, 'w') as f:
            f.write()

    def update_web_config(self, delete=False):
        if delete:
            os.remove(WEB_CONFIG)
            return

        with open(WEB_CONFIG) as f:
            content = [l for l in f]

        content.insert(3, WEB_CONFIG_STRING)

        with open(WEB_CONFIG, 'w') as f:
            f.write(''.join(content))

    def set_project_permissions(self, filename):
        # set permissions on the root project directory for the IIS site user
        cmd = ['ICACLS', get_project_root(), '/t', '/grant',
               'IIS AppPool\{}:F'.format(settings.INSTANCE_NAME)]
        subprocess.check_call(cmd)

    def handle(self, *args, **options):
            self.setup_static_assets(delete=options.get('delete'))
            self.create_touch_file(delete=options.get('delete'))

            winfcgi_install.set_file_readable = \
                self.set_project_permissions

            management.call_command(winfcgi_install.Command(
                site_name=settings.INSTANCE_NAME,
                monitor_changes_to=TOUCH_FILE,
                binding='{}://{}:{}'.format(
                    'https',
                    settings.SITE_DOMAIN_NAME,
                    443,
                ),
                delete=options.get('delete'),
                maxContentLength=MAX_CONTENT_LENGTH,
            ))

            self.update_web_config(delete=options.get('delete'))
            #self.set_project_permissions()

            # call command celerytask
            management.call_command(celerytask.Command(
                delete=options.get('delete'))
            )

            print('''
PLEASE NOTE: This command is unable to set
the certificate to use for the specified binding.
Please use the IIS tool to edit the binding and
set the correct certificate:

1) Open IIS
2) Expand the "Sites" in the left navigation panel
3) Right-click "{}" and choose "Edit Bindings"
4) Edit the binding and choose the correct SSL Certificate'''.format(
                settings.INSTANCE_NAME)
            )
