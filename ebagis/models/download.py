from __future__ import absolute_import

import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import transaction
from django.contrib.gis.db import models

from celery import states

from djcelery.models import TaskMeta

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
                             editable=False,
                             on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id',
                                       for_concrete_model=False)
    task = models.ForeignKey(TaskMeta, related_name='download',
                             null=True, blank=True, on_delete=models.CASCADE)
    file = models.FileField(max_length=255, null=True, blank=True)
    # TODO: need a way to pass in a date to this
    querydate = models.DateTimeField(default=timezone.now)

    @property
    def filename(self):
        return self.content_object._archive_name

    @property
    def expires_at(self):
        return self.created_at + settings.EXPIRATION_DELTA

    @property
    def expired(self):
        return self.expires_at <= timezone.now()

    @property
    def nstatus(self):
        if self.task.status == states.SUCCESS:
            status = 'COMPLETED'
        elif self.task.status == states.PENDING:
            status = 'QUEUED'
        elif self.task.status in [states.RETRY, states.STARTED]:
            status = 'PROCESSING'
        elif self.task.status == states.FAILURE:
            status = 'FAILED'
        elif self.task.status in ['ABORTED', states.REVOKED]:
            status = 'CANCELLED'
        else:
            status = 'UNKNOWN'
        return status

    def delete_file(self):
        if self.file:
            storage, path = self.file.storage, self.file.path
            storage.delete(path)

    @transaction.atomic
    def delete(self, remove_file=True, *args, **kwargs):
        super(Download, self).delete(*args, **kwargs)
        if remove_file:
            self.delete_file()
