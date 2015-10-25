from __future__ import absolute_import
import os
import shutil
import uuid

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.gis.db import models

from djcelery.models import TaskMeta

from ..settings import DOWNLOADS_DIRECTORY, EXPIRATION_DELTA

from .mixins import DateMixin


class Download(DateMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User,
                             related_name="%(class)s",
                             editable=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id',
                                       for_concrete_model=False)
    task = models.ForeignKey(TaskMeta, related_name='download',
                             null=True, blank=True)
    file = models.FileField(max_length=255, null=True, blank=True)
    # TODO: need a way to pass in a date to this
    querydate = models.DateTimeField(default=timezone.now)

    @property
    def expires_at(self):
        return self.created_at + EXPIRATION_DELTA

    @property
    def expired(self):
        return self.expires_at <= timezone.now()

    def delete(self, remove_file=True, *args, **kwargs):
        super(Download, self).delete(*args, **kwargs)
        if remove_file:
            shutil.rmtree(os.path.join(DOWNLOADS_DIRECTORY,
                                       self.id))
