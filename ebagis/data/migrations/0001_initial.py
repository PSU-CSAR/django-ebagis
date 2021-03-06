# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-10 03:43
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AOI',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('removed_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('comment', models.TextField(blank=True)),
                ('shortname', models.CharField(max_length=25)),
                ('boundary', django.contrib.gis.db.models.fields.MultiPolygonField(geography=True, srid=4326)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ebagis_data_aoi_created_by', to=settings.AUTH_USER_MODEL)),
                ('parent_aoi', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_aois', to='ebagis_data.AOI')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('removed_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('classname', models.CharField(max_length=40)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('comment', models.TextField(blank=True)),
                ('archiving_rule', models.CharField(choices=[(b'NONE', b'No Archiving'), (b'INDIVIDUAL', b'Individual Archiving'), (b'GROUP', b'Group Archiving'), (b'READONLY', b'Read Only (No Archiving)')], default=b'NONE', editable=False, max_length=10)),
                ('_parent_directory', models.CharField(max_length=1000)),
                ('_parent_object', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subdirectories', to='ebagis_data.Directory')),
                ('aoi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='directory', to='ebagis_data.AOI')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ebagis_data_directory_created_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('removed_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('classname', models.CharField(max_length=40)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('comment', models.TextField(blank=True)),
                ('_parent_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='ebagis_data.Directory')),
                ('aoi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file', to='ebagis_data.AOI')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ebagis_data_file_created_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FileData',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('removed_at', models.DateTimeField(blank=True, null=True)),
                ('classname', models.CharField(max_length=40)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('comment', models.TextField(blank=True)),
                ('encoding', models.CharField(blank=True, max_length=20, null=True)),
                ('sha256', models.CharField(max_length=64)),
                ('_parent_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='ebagis_data.File')),
                ('aoi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filedata', to='ebagis_data.AOI')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ebagis_data_filedata_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PourPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('location', django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326)),
                ('boundary', django.contrib.gis.db.models.fields.MultiPolygonField(geography=True, null=True, srid=4326)),
                ('boundary_simple', django.contrib.gis.db.models.fields.MultiPolygonField(geography=True, null=True, srid=4326)),
                ('awdb_id', models.CharField(blank=True, max_length=30, null=True)),
                ('source', models.PositiveSmallIntegerField(choices=[(1, b'Reference Point'), (2, b'AWDB Point'), (3, b'Imported AOI Point')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='aoi',
            name='pourpoint',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='aois', to='ebagis_data.PourPoint'),
        ),
        migrations.CreateModel(
            name='AOIDirectory',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.directory',),
        ),
        migrations.CreateModel(
            name='Geodatabase',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.directory',),
        ),
        migrations.CreateModel(
            name='HRUZones',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.directory',),
        ),
        migrations.CreateModel(
            name='HRUZonesData',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.directory',),
        ),
        migrations.CreateModel(
            name='Layer',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.file',),
        ),
        migrations.CreateModel(
            name='LayerData',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.filedata',),
        ),
        migrations.CreateModel(
            name='Maps',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.directory',),
        ),
        migrations.CreateModel(
            name='PrismDir',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.directory',),
        ),
        migrations.CreateModel(
            name='Zones',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.directory',),
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together=set([('_parent_object', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='directory',
            unique_together=set([('_parent_object', 'name')]),
        ),
        migrations.CreateModel(
            name='Geodatabase_GroupArchive',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.geodatabase',),
        ),
        migrations.CreateModel(
            name='Geodatabase_IndividualArchive',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.geodatabase',),
        ),
        migrations.CreateModel(
            name='Geodatabase_ReadOnly',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.geodatabase',),
        ),
        migrations.CreateModel(
            name='Raster',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.layer',),
        ),
        migrations.CreateModel(
            name='RasterData',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.layerdata',),
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.layer',),
        ),
        migrations.CreateModel(
            name='TableData',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.layerdata',),
        ),
        migrations.CreateModel(
            name='Vector',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.layer',),
        ),
        migrations.CreateModel(
            name='VectorData',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.layerdata',),
        ),
        migrations.CreateModel(
            name='Analysis',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.geodatabase_individualarchive',),
        ),
        migrations.CreateModel(
            name='AOIdb',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.geodatabase_readonly',),
        ),
        migrations.CreateModel(
            name='HRUZonesGDB',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.geodatabase_readonly',),
        ),
        migrations.CreateModel(
            name='Layers',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.geodatabase_individualarchive',),
        ),
        migrations.CreateModel(
            name='ParamGDB',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.geodatabase_readonly',),
        ),
        migrations.CreateModel(
            name='Prism',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.geodatabase_grouparchive',),
        ),
        migrations.CreateModel(
            name='Surfaces',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('ebagis_data.geodatabase_readonly',),
        ),
    ]
