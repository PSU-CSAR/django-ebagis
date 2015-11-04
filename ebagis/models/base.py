from __future__ import absolute_import
import uuid

from django.contrib.gis.db import models

from rest_framework.reverse import reverse


class ABC(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.TextField(blank=True)
    _singular = False

    @property
    def _classname(self):
        return self.__class__.__name__.lower()

    @property
    def _plural_name(self):
        return self._classname + "s"

    @property
    def _parent_object(self):
        return None

    def get_url(self, request, no_model_name=False, no_s=False):
        pk = str(self.pk)
        #if not self._parent_object:
        #    view = self._classname + "-base:detail"
        #    kwargs = {"pk": pk}
        #    return reverse(view, kwargs=kwargs, request=request)

        #url = self._parent_object.get_url(request)

        #if self._singular:
        #    url += "{}/".format(self._classname)
        #elif no_model_name:
        #    url += "{}/".format(pk)
        #else:
        #    name = self._classname if no_s else self._plural_name
        #    url += "{}/{}/".format(name, pk)

        #return url

        view = self._classname + "-base:detail"
        kwargs = {"pk": pk}
        return reverse(view, kwargs=kwargs, request=request)

    class Meta:
        abstract = True
