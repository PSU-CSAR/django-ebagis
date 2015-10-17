from __future__ import absolute_import

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models

from djcelery.models import TaskMeta

from drf_chunked_upload.models import ChunkedUpload


class Upload(ChunkedUpload):
    content_type = models.ForeignKey(ContentType)
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id',
                                       for_concrete_model=False)
    is_update = models.BooleanField(default=False)
    parent_object_content_type = \
        models.ForeignKey(ContentType, related_name="upload_parent",
                          null=True, blank=True)
    parent_object_id = models.UUIDField(null=True, blank=True)
    parent_object = GenericForeignKey('parent_object_content_type',
                                      'parent_object_id',
                                      for_concrete_model=False)
    comment = models.TextField(blank=True)
    task = models.ForeignKey(TaskMeta, related_name='aoi_upload',
                             null=True, blank=True)
