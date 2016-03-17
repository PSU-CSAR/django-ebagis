from __future__ import absolute_import
import os
import uuid

from django.contrib.gis.db import models

from rest_framework.reverse import reverse

from ..utils.metadata import write_metadata


class ABC(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.TextField(blank=True)
    _singular = False

    # use this dict to store the field names for fields that should be
    # written to a metadata file for the object in the file system
    # fields that should not change are read_only, while fields that
    # need to be watched for changes should be writable
    # if no fields are specified, then no metadata operations
    # will be performed.
    _archive_fields = {"read_only": [], "writable": []}

    # override this for all subclasses as required
    path = None

    @property
    def _classname(self):
        return self.__class__.__name__.lower()

    @property
    def _plural_name(self):
        return self._classname + "s"

    @property
    def _parent_object(self):
        return None

    @property
    def _has_metadata(self):
        return bool(self._archive_fields["read_only"] and
                    self._archive_fields["writable"] and
                    self._metadata_path)

    @property
    def _metadata_path(self):
        return self.path

    def save(self, to_update=False, *args, **kwargs):
        """overriding the default save method to allow
        metadata creation/updates for models with archive fields
        """
        # if a writable field has been updated, then we also
        # know we need to update the metadata file
        # however, if it is a new model, we are by default updating,
        # and we can know it is new if it does not have the original
        # values attribute
        if self._has_metadata and not hasattr(self, "_original_values"):
            to_update = True
        # otherwise let's check to see if any fields have changed
        # also, we can check to_update first as a slight optimization
        elif self._has_metadata and not to_update:
            for field in self._archive_fields["writable"]:
                if getattr(self, field) != self._original_values[field]:
                    to_update = True
                    # no need in checking the other fields
                    break

        # now let's do our normal save stuff
        saved = super(ABC, self).save(*args, **kwargs)

        # if to_update then we need to update the XML metadata file
        if self._has_metadata and to_update:
            dict_to_write = {}
            # we'll get the values for the fields from the lists
            # in the field dict, though we have to do some funny
            # business to flatten the two lists together
            for field in [x for y in self._archive_fields.values() for x in y]:
                dict_to_write[field] = getattr(self, field)
            # and we'll use our metadata module to make the changes
            write_metadata(self._metadata_path, dict_to_write)

        # now let's return the output from the super'd save method
        return saved

    @classmethod
    def from_db(cls, db, field_names, values, *args, **kwargs):
        """django-approved method for getting a copy of a field
        on DB read; this is useful for determining if a field's
        value has been changed without another DB request"""
        # call the original from_db method
        instance = super(ABC, cls).from_db(
            db, field_names, values, *args, **kwargs
        )
        # now add the "writable" field values to
        # a dict on the returned model instance
        instance._original_values = {
            key: dict(zip(field_names, values))
            for key in cls._archive_fields["writable"]
        }
        # return the modified model instance
        return instance

    def get_url(self, request, no_model_name=False, no_s=False):
        pk = str(self.pk)

        # the following bit of code is used to resolve object URLs
        # with heirarchy. It is not currently needed, but
        # am not certain if I am going to keep the current behavior
        # or revert to this method

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

        # this simply returns the URL directly to the object
        view = self._classname + "-base:detail"
        kwargs = {"pk": pk}
        return reverse(view, kwargs=kwargs, request=request)

    class Meta:
        abstract = True
