# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-03-05 05:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ebagis', '0006_add_pourpoints'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='offset',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='upload',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Incomplete'), (2, b'Complete')], default=1),
        ),
    ]
