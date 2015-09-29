from __future__ import absolute_import
import os
import uuid

from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation,
    )
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.gis.db import models
from django.db import transaction

from rest_framework.reverse import reverse

from ..constants import URL_FILTER_QUERY_ARG_PREFIX, MULTIPLE_GDBS

from .base import ABC
from .mixins import ProxyMixin, DateMixin, NameMixin, AOIRelationMixin
from .file_data import FileData, XMLData, MapDocumentData, LAYER_DATA_CLASSES


class File(ProxyMixin, DateMixin, NameMixin, AOIRelationMixin, ABC):
    content_type = models.ForeignKey(ContentType)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    versions = GenericRelation(FileData, for_concrete_model=False)

    class Meta:
        unique_together = ("content_type", "object_id", "name")

    @prooperty
    def _parent_object(self):
        return self.content_object

    @classmethod
    @transaction.atomic
    def create(cls, input_file, containing_object, user,
               data_class=FileData, id=None):
        content_type = ContentType.objects.get_for_model(
            containing_object.__class__,
            for_concrete_model=False
        )
        file_name = os.path.splitext(os.path.basename(input_file))[0]
        file_obj = cls(aoi=containing_object.aoi,
                       content_type=content_type,
                       object_id=containing_object.id,
                       name=file_name,
                       id=id)
        file_obj.save()
        data_class.create(input_file, file_obj, user)
        return file_obj

    @transaction.atomic
    def update(self):
        raise NotImplementedError

    def export(self, output_dir, querydate=timezone.now()):
        super(File, self).export(output_dir, querydate)
        query = self.versions.filter(created_at__lte=querydate)
        return query.latest("created_at").export(output_dir)


class XML(File):
    class Meta:
        proxy = True

    @property
    def _singular(self):
        is_single = False
        if self.content_object._classname == "hru":
            is_single = True
        return True

    @classmethod
    @transaction.atomic
    def create(cls, input_file, containing_object, user, id=None):
        return super(XML, cls).create(input_file,
                                      containing_object,
                                      user,
                                      data_class=XMLData,
                                      id=id)


class MapDocument(File):
    class Meta:
        proxy = True

    def get_url(self, request):
        if not self.aoi:
            return super(File, self).get_url(request)
        url = self.aoi.get_url()
        url += self._classname + "s/" + self.pk
        return url

    @classmethod
    @transaction.atomic
    def create(cls, input_file, containing_object, user, id=None):
        return super(MapDocument, cls).create(input_file,
                                              containing_object,
                                              user,
                                              data_class=MapDocumentData,
                                              id=id)


class Layer(File):
    class Meta:
        proxy = True

    @classmethod
    @transaction.atomic
    def create(cls, arcpy_ext_layer, geodatabase, user, id=None):
        content_type = ContentType.objects.get_for_model(
            geodatabase.__class__,
            for_concrete_model=False
        )
        file_obj = cls(aoi=geodatabase.aoi,
                       content_type=content_type,
                       object_id=geodatabase.id,
                       name=arcpy_ext_layer.name,
                       id=id)
        file_obj.save()
        LAYER_DATA_CLASSES[arcpy_ext_layer.type].create(arcpy_ext_layer,
                                                        file_obj,
                                                        user)
        return file_obj


class Vector(Layer):
    class Meta:
        proxy = True


class Raster(Layer):
    class Meta:
        proxy = True


class Table(Layer):
    class Meta:
        proxy = True
