# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import drf_chunked_upload.models
import django.contrib.gis.db.models.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('djcelery', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AOI',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, editable=False, max_length=10, unique=True, db_index=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('removed_at', models.DateTimeField(null=True, blank=True)),
                ('shortname', models.CharField(max_length=25)),
                ('directory_path', models.CharField(max_length=1000)),
                ('boundary', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'abstract': False,
                'get_latest_by': 'created_at',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AOIUpload',
            fields=[
                ('id', models.CharField(primary_key=True, default=drf_chunked_upload.models.generate_id, serialize=False, editable=False, max_length=32, unique=True)),
                ('file', models.FileField(max_length=255, upload_to=drf_chunked_upload.models.generate_filename)),
                ('filename', models.CharField(max_length=255)),
                ('offset', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.PositiveSmallIntegerField(default=1, choices=[(1, 'Uploading'), (2, 'Complete'), (3, 'Failed')])),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('task', models.ForeignKey(related_name='aoi_upload', blank=True, to='djcelery.TaskMeta', null=True)),
                ('user', models.ForeignKey(related_name='aoiupload', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, editable=False, max_length=10, unique=True, db_index=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('removed_at', models.DateTimeField(null=True, blank=True)),
                ('aoi', models.ForeignKey(related_name='directory_related', to='ebagisapp.AOI')),
                ('created_by', models.ForeignKey(related_name='ebagisapp_directory_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Geodatabase',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, editable=False, max_length=10, unique=True, db_index=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('removed_at', models.DateTimeField(null=True, blank=True)),
                ('aoi', models.ForeignKey(related_name='geodatabase_related', to='ebagisapp.AOI')),
                ('created_by', models.ForeignKey(related_name='ebagisapp_geodatabase_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MapDocument',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, editable=False, max_length=10, unique=True, db_index=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('removed_at', models.DateTimeField(null=True, blank=True)),
                ('filename', models.CharField(max_length=1250)),
                ('encoding', models.CharField(max_length=20, null=True, blank=True)),
                ('object_id', models.CharField(max_length=10)),
                ('aoi', models.ForeignKey(related_name='mapdocument_related', to='ebagisapp.AOI')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(related_name='ebagisapp_mapdocument_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Raster',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, editable=False, max_length=10, unique=True, db_index=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('removed_at', models.DateTimeField(null=True, blank=True)),
                ('filename', models.CharField(max_length=1250)),
                ('encoding', models.CharField(max_length=20, null=True, blank=True)),
                ('object_id', models.CharField(max_length=10)),
                ('srs_wkt', models.CharField(max_length=1000)),
                ('resolution', models.FloatField()),
                ('aoi', models.ForeignKey(related_name='raster_related', to='ebagisapp.AOI')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(related_name='ebagisapp_raster_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, editable=False, max_length=10, unique=True, db_index=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('removed_at', models.DateTimeField(null=True, blank=True)),
                ('filename', models.CharField(max_length=1250)),
                ('encoding', models.CharField(max_length=20, null=True, blank=True)),
                ('object_id', models.CharField(max_length=10)),
                ('aoi', models.ForeignKey(related_name='table_related', to='ebagisapp.AOI')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(related_name='ebagisapp_table_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UpdateUpload',
            fields=[
                ('id', models.CharField(primary_key=True, default=drf_chunked_upload.models.generate_id, serialize=False, editable=False, max_length=32, unique=True)),
                ('file', models.FileField(max_length=255, upload_to=drf_chunked_upload.models.generate_filename)),
                ('filename', models.CharField(max_length=255)),
                ('offset', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.PositiveSmallIntegerField(default=1, choices=[(1, 'Uploading'), (2, 'Complete'), (3, 'Failed')])),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('object_id', models.CharField(max_length=10)),
                ('processed', models.TextField(default=b'No')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('user', models.ForeignKey(related_name='updateupload', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vector',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, editable=False, max_length=10, unique=True, db_index=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('removed_at', models.DateTimeField(null=True, blank=True)),
                ('filename', models.CharField(max_length=1250)),
                ('encoding', models.CharField(max_length=20, null=True, blank=True)),
                ('object_id', models.CharField(max_length=10)),
                ('srs_wkt', models.CharField(max_length=1000)),
                ('geom_type', models.CharField(max_length=50)),
                ('aoi', models.ForeignKey(related_name='vector_related', to='ebagisapp.AOI')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(related_name='ebagisapp_vector_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='XML',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, editable=False, max_length=10, unique=True, db_index=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('removed_at', models.DateTimeField(null=True, blank=True)),
                ('filename', models.CharField(max_length=1250)),
                ('encoding', models.CharField(max_length=20, null=True, blank=True)),
                ('object_id', models.CharField(max_length=10)),
                ('aoi', models.ForeignKey(related_name='xml_related', to='ebagisapp.AOI')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(related_name='ebagisapp_xml_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='aoi',
            name='analysis',
            field=models.OneToOneField(related_name='aoi_analysis', null=True, blank=True, to='ebagisapp.Geodatabase'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aoi',
            name='aoidb',
            field=models.OneToOneField(related_name='aoi_aoidb', null=True, blank=True, to='ebagisapp.Geodatabase'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aoi',
            name='created_by',
            field=models.ForeignKey(related_name='ebagisapp_aoi_created_by', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aoi',
            name='hruzones',
            field=models.ManyToManyField(related_name='aoi_hruzones', null=True, to='ebagisapp.Geodatabase', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aoi',
            name='layers',
            field=models.OneToOneField(related_name='aoi_layers', null=True, blank=True, to='ebagisapp.Geodatabase'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aoi',
            name='maps',
            field=models.ManyToManyField(related_name='aoi_maps', null=True, to='ebagisapp.MapDocument', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aoi',
            name='prism',
            field=models.OneToOneField(related_name='aoi_prism', null=True, blank=True, to='ebagisapp.Geodatabase'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aoi',
            name='surfaces',
            field=models.OneToOneField(related_name='aoi_surfaces', null=True, blank=True, to='ebagisapp.Geodatabase'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Analysis',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('ebagisapp.geodatabase',),
        ),
        migrations.CreateModel(
            name='AOIdb',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('ebagisapp.geodatabase',),
        ),
        migrations.CreateModel(
            name='HRUZones',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('ebagisapp.geodatabase',),
        ),
        migrations.CreateModel(
            name='Layers',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('ebagisapp.geodatabase',),
        ),
        migrations.CreateModel(
            name='Maps',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('ebagisapp.directory',),
        ),
        migrations.CreateModel(
            name='Prism',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('ebagisapp.geodatabase',),
        ),
        migrations.CreateModel(
            name='Surfaces',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('ebagisapp.geodatabase',),
        ),
    ]
