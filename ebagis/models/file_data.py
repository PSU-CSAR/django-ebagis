from __future__ import absolute_import
import os
import shutil
import logging

from django.contrib.gis.db import models

from .. import constants
from ..utils import transaction
from ..utils.validation import hash_file, generate_uuid, sanitize_uuid

from .base import ABC
from .mixins import (
    ProxyMixin, DateMixin, CreatedByMixin, AOIRelationMixin,
)


logger = logging.getLogger(__name__)


class FileData(ProxyMixin, DateMixin, CreatedByMixin,
               AOIRelationMixin, ABC):
    encoding = models.CharField(max_length=20, null=True, blank=True)
    _parent_object = models.ForeignKey('File',
                                       related_name='versions',
                                       on_delete=models.CASCADE)

    # we are using sha256 for file hashes; others would suffice,
    # but sha256 has less collisions so is a little bit safer
    sha256 = models.CharField(max_length=64)

    # lists of field names to be written to the XML metadata file
    # we only need those that cannot be recreated, though
    # the hash of the file is included as it might prove
    # useful for version detection later on
    _archive_fields = {
        "read_only": ["id", "created_at", "created_by",
                      "sha256", "_parent_object"],
        "writable": ["comment"]
    }

    @property
    def parent_object(self):
        return self._parent_object

    @property
    def ext(self):
        return "." + os.path.splitext(self.name)[1]

    @property
    def directory(self):
        return self._parent_object.parent_directory

    @property
    def _path_name(self):
        return str(self.id) + self.ext

    @property
    def path(self):
        return os.path.join(self.directory, self._path_name)

    @property
    def name(self):
        return self._parent_object.name

    def save(self, src=None, *args, **kwargs):
        to_update = False

        if src:
            self.id = kwargs.get('id', generate_uuid(self.__class__))
            self._copy_file(src)

        if not self.sha256:
            # if the hash has never been calc'd, we know this is a
            # new record and we need to update the metadata file,
            # and we of course know we need to hash the file
            self.sha256 = hash_file(self.path)
            to_update = True

        return super(FileData, self).save(*args, to_update=to_update, **kwargs)

    def _copy_file(self, src):
        shutil.copy(src, self.path)

    @classmethod
    @transaction.atomic
    def create(cls, input_file, File, user, id=None, comment=""):
        data_obj = cls(aoi=File.aoi,
                       _parent_object=File,
                       created_by=user,
                       id=id,
                       comment=comment)
        data_obj.save(src=input_file)
        return data_obj

    def export(self, output_dir, name=None, copy_function=shutil.copy):
        if not name:
            name = self.name
        copy_function(self.path, os.path.join(output_dir, name))


class LayerData(FileData):
    ext = ""

    class Meta:
        proxy = True

    @property
    def _path_name(self):
        return sanitize_uuid(str(self.id)) + self.ext

    @classmethod
    @transaction.atomic
    def create(cls, arcpy_ext_layer, File, user, id=None, comment=""):
        data_obj = cls(aoi=File.aoi,
                       _parent_object=File,
                       created_by=user,
                       id=id,
                       comment=comment)
        data_obj.save(src=arcpy_ext_layer)
        return data_obj

    def _copy_file(self, src):
        src.copy_to_file(self.directory,
                         outname=sanitize_uuid(str(self.id)))


class VectorData(LayerData):
    ext = constants.FC_EXT

    class Meta:
        proxy = True

    def export(self, output_dir, name=None):
        from arcpy.management import CopyFeatures
        super(VectorData, self).export(output_dir, name, CopyFeatures)


class RasterData(LayerData):
    ext = constants.RASTER_EXT

    class Meta:
        proxy = True

    def export(self, output_dir, name=None):
        from arcpy.management import CopyRaster
        super(RasterData, self).export(output_dir, name, CopyRaster)


class TableData(LayerData):
    ext = constants.TABLE_EXT

    class Meta:
        proxy = True

    def export(self, output_dir, name=None):
        from arcpy.management import CopyRows
        super(TableData, self).export(output_dir, name, CopyRows)


# used in the Layer class to find the proper data class to go
# with a given layer data type
LAYER_DATA_CLASSES = {
    constants.FC_TYPECODE: VectorData,
    constants.RASTER_TYPECODE: RasterData,
    constants.TABLE_TYPECODE: TableData,
}
