from __future__ import absolute_import
import uuid

from django.contrib.gis.db import models


class ABC(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.TextField(blank=True)
    _singular = False

    @property
    def _classname(self):
        return self.__class__.__name__.lower()

    @property
    def _parent_object(self):
        raise NotImplementedError

    def get_url(self, request, no_model_name=False):
        if not self._parent_object:
            view = self._classname + "-base:detail"
            kwargs = {"pk": self.pk}
            return reverse(view, kwargs, request)

        url = self._parent_object.get_url()

        if self._singular:
            url += self._classname
        elif no_model_name:
            url += self.pk
        else:
            url += self._classname + "s/" + self.pk

        return url

    class Meta:
        abstract = True

