# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-19 03:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import drf_chunked_upload.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('djcelery', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Download',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('removed_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('object_id', models.UUIDField()),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=b'')),
                ('querydate', models.DateTimeField(default=django.utils.timezone.now)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='download', to='djcelery.TaskMeta')),
            ],
            options={
                'abstract': False,
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='ExpiringToken',
            fields=[
                ('key', models.CharField(max_length=40, unique=True, verbose_name='Key')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='token', serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='User')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
            ],
            options={
                'verbose_name': 'Token',
                'verbose_name_plural': 'Tokens',
            },
        ),
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(max_length=255, null=True, upload_to=drf_chunked_upload.models.generate_filename)),
                ('filename', models.CharField(max_length=255)),
                ('offset', models.BigIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, b'Incomplete'), (2, b'Complete')], default=1)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('object_id', models.UUIDField(blank=True, null=True)),
                ('is_update', models.BooleanField(default=False)),
                ('parent_object_id', models.UUIDField(blank=True, null=True)),
                ('comment', models.TextField(blank=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('parent_object_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upload_parent', to='contenttypes.ContentType')),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upload', to='djcelery.TaskMeta')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='upload', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='download',
            name='user',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='download', to=settings.AUTH_USER_MODEL),
        ),
    ]
