# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


def create_nwcc_user_groups(apps, schema_editor):
    from ebagis.apps import create_or_update_nwcc_user_groups
    create_or_update_nwcc_user_groups()


def load_userdata_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "prod_users")


class Migration(migrations.Migration):

    dependencies = [
        ('ebagis', '0002_load_pourpoints'),
    ]

    operations = [
        migrations.RunPython(create_nwcc_user_groups),
        migrations.RunPython(load_userdata_from_fixture),
    ]
