from __future__ import absolute_import

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models

from djcelery.models import TaskMeta

from drf_chunked_upload.models import ChunkedUpload


class AOIUpload(ChunkedUpload):
    comment = models.TextField(blank=True)
    task = models.ForeignKey(TaskMeta, related_name='aoi_upload',
                             null=True, blank=True)


class UpdateUpload(ChunkedUpload):
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=10)
    content_object = GenericForeignKey('content_type', 'object_id')
    processed = models.TextField(default="No")
