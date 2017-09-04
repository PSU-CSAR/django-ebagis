from __future__ import absolute_import

import os

from django.utils import timezone
from django.contrib.gis.db import models

from ebagis.utils import transaction
from ebagis.utils.validation import hash_file

from .base import ABC
from ebagis.models.mixins import (
    ProxyMixin, DateMixin, NameMixin, AOIRelationMixin, CreatedByMixin
)

from .file_data import (
    FileData, LAYER_DATA_CLASSES
)


class File(ProxyMixin, CreatedByMixin, DateMixin,
           NameMixin, AOIRelationMixin, ABC):
    _parent_object = models.ForeignKey('Directory',
                                       related_name='files',
                                       on_delete=models.CASCADE)
    _prefetch = ["versions"]

    _archive_fields = {"read_only": ["id", "created_at", "created_by"],
                       "writable": ["name", "comment"]}

    class Meta:
        unique_together = ("_parent_object", "name")

    @property
    def parent_object(self):
        return self._parent_object

    @property
    def parent_directory(self):
        return self._parent_object.path

    @classmethod
    @transaction.atomic
    def create(cls, input_file, parent_directory_object, user,
               data_class=FileData, id=None, comment=""):
        file_name = os.path.basename(input_file)
        file_obj = cls(aoi=parent_directory_object.aoi,
                       _parent_object=parent_directory_object,
                       name=file_name,
                       created_by=user,
                       id=id,
                       comment=comment)
        file_obj.save()
        data_class.create(input_file, file_obj, user)
        return file_obj

    @transaction.atomic
    def update(self):
        raise NotImplementedError

    # TODO: this is not handling the file ext correctly
    # probably need to add another property to the class
    # for the file extension and add that to the string
    @property
    def _export_name(self):
        return self.name

    @property
    def _archive_name(self):
        return "{}-{}".format(self.aoi.name, self._export_name)

    @property
    def aoi_path(self):
        return os.path.join(self.parent_object.aoi_path, self._export_name)

    def export(self, output_dir, querydate=timezone.now(),
               create_heirarchy=False):
        self._validate_querydate(querydate)
        query = self.versions.filter(created_at__lte=querydate)
        return_path = output_dir

        if create_heirarchy:
            return_path = os.path.join(output_dir, self._archive_name)
            output_dir = os.path.join(return_path,
                                      os.path.dirname(self.aoi_path))
            os.makedirs(output_dir)

        query.latest("created_at").export(output_dir, self.name)

        return return_path

    def is_new_version(self, file_path):
        sha = hash_file(file_path)
        for version in self.versions:
            if sha == version.sha_hash:
                return False
        return True


class Layer(File):
    class Meta:
        proxy = True

    @classmethod
    @transaction.atomic
    def create(cls, arcpy_ext_layer, geodatabase, user,
               id=None, comment=""):
        file_obj = cls(aoi=geodatabase.aoi,
                       _parent_object=geodatabase,
                       name=arcpy_ext_layer.name,
                       created_by=user,
                       id=id,
                       comment=comment)
        file_obj.save()
        LAYER_DATA_CLASSES[arcpy_ext_layer.type].create(arcpy_ext_layer,
                                                        file_obj,
                                                        user)
        return file_obj

    def export(self, output_dir, querydate=timezone.now(),
               create_heirarchy=False):
        self._validate_querydate(querydate)
        query = self.versions.filter(created_at__lte=querydate)
        return_path = None

        if create_heirarchy:
            return_path = os.path.join(output_dir, self._archive_name)
            output_dir = \
                self.parent_object.layer_export_create_gdb(return_path)

        query.latest('created_at').export(output_dir, self.name)

        return return_path


class Vector(Layer):
    class Meta:
        proxy = True


class Raster(Layer):
    class Meta:
        proxy = True


class Table(Layer):
    class Meta:
        proxy = True
