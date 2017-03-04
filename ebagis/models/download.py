from __future__ import absolute_import
import os
import shutil
import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.gis.db import models

from djcelery.models import TaskMeta

from ..settings import DOWNLOADS_DIRECTORY, EXPIRATION_DELTA

from .mixins import DateMixin, NameMixin

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


# The name field is not strictly required--it seems that I should
# be able to query based on the generic foreign key. However, in some
# cases it seems the reverse relation needs to exist (generic relation)
# but that is complicated. So I chose just to put the name field on the
# download model via the NameMixin.
class Download(DateMixin, NameMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AUTH_USER_MODEL,
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
