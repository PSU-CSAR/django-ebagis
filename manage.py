#!/usr/bin/env python
from __future__ import absolute_import, print_function

import os
import sys


CONF_FILE = os.path.join(os.path.dirname(__file__), 'project.conf')


def activate_help():
    import yaml
    with open(CONF_FILE) as f:
        instance_name = yaml.load(f)['INSTANCE_NAME']
    return (
        'ERROR: ebagis.settings could not be imported.\n'
        'It looks like you need to activate the conda environment '
        'for this instance, which you can do by running '
        '`activate {}`'.format(instance_name)
    )


def install(help=False):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    # first we append the path with the management package
    # so we can import utils in the install module
    sys.path.append(
        os.path.join(
            this_dir,
            'ebagis',
            'management',
        )
    )
    # then we add the commands package to the path
    # so we have access to the install module
    sys.path.append(
        os.path.join(
            this_dir,
            'ebagis',
            'management',
            'commands',
        )
    )
    # and lastly we add the directory of this file
    # to the path so we can import from setup.py
    sys.path.append(
        os.path.join(
            this_dir,
        )
    )
    from install import Install
    if help:
        Install.print_help(sys.argv[0], sys.argv[2])
    else:
        Install.run_from_argv(sys.argv)


def default_django_command():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ebagis.settings")

    # check to make sure we can import the settings
    # otherwise, we suspect the env has not been activated
    try:
        import ebagis.settings
    except ImportError:
        print(activate_help())
        return 1

    # hacky workaround to allow ebagis command to use the
    # autoreloader with the runserver and runcelery commands
    # (problem is that the reload uses subprocess to call
    # sys.executable with the sys.argv[0] as its first arg,
    # which means effectively means it calls `python ebagis ...`,
    # which fails either because ebagis cannot be found, or
    # ebagis is found, and it is the ebagis package in the
    # current directory.)
    if len(sys.argv) > 1 and \
            sys.argv[1] == 'runserver' and \
            not ('--help' in sys.argv or '-h' in sys.argv):
        sys.argv[0] = __file__

    #if os.path.basename(sys.argv[0]) == 'ebagis':
    #    sys.argv[0] = 'ebagis'
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'install':
        return install()
    if len(sys.argv) > 1 and \
            os.path.basename(sys.argv[0]) == 'manage.py' and \
            sys.argv[1] == 'help' and \
            sys.argv[2] == 'install':
        return install(help=True)
    elif not os.path.isfile(CONF_FILE):
        print('ERROR: Could not find configuration file {}.'.format(CONF_FILE))
        print('Has this instance been installed? '
              'Try running `python manage.py install`.')
    else:
        return default_django_command()


if __name__ == "__main__":
    sys.exit(main())
