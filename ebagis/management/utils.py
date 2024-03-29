from __future__ import absolute_import

import os
import random
import string


SETTINGS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    'settings',
)


def get_default(dictionary, key, default=None):
    val = dictionary.get(key, None)
    return val if val is not None else default


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


def get_project_root():
    # path should look something like
    # d:\development\ebagis_dev\django-ebagis\ebagis\settings
    # which should be split into separate elements in a list
    # the project root is 4th from the end, which we use to slice and
    # reconstruct into d:\development\ebagis_dev\django-ebagis
    return os.path.join(*destruct_path(SETTINGS_DIR)[:-2])


def get_instance_name():
    try:
        # path should look something like
        # d:\development\ebagis_dev\django-ebagis\ebagis\settings
        # which should be split into separate elements in a list
        # the instance name is 5th from the end (ebagis_dev)
        return destruct_path(SETTINGS_DIR)[-4]
    except IndexError:
        # path was too short and we couldn't get anything from it
        return None


def get_env_name():
    try:
        # path should look something like
        # d:\development\ebagis_dev\django-ebagis\ebagis\settings
        # which should be split into separate elements in a list
        # the instance name is 6th from the end (development)
        return destruct_path(SETTINGS_DIR)[-5]
    except IndexError:
        # path was too short and we couldn't get anything from it
        return None


def get_settings_file(file_name=None):
    if file_name:
        return os.path.join(
            SETTINGS_DIR,
            file_name,
        )
    return SETTINGS_DIR
