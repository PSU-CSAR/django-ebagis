from __future__ import absolute_import
import os
import shutil
from logging import exception

from django.utils import timezone
from django.contrib.gis.db import models

from .. import constants
from ..utils import transaction
from ..utils.validation import hash_file, generate_uuid, sanitize_uuid

from .base import ABC
from .mixins import (
    ProxyMixin, DateMixin, CreatedByMixin, AOIRelationMixin,
)


class FileData(ProxyMixin, DateMixin, CreatedByMixin,
               AOIRelationMixin, ABC):
    path = models.CharField(max_length=1024, unique=True)
    encoding = models.CharField(max_length=20, null=True, blank=True)
    _parent_object = models.ForeignKey('File',
                                       related_name='versions',
                                       on_delete=models.CASCADE)

    # we are using sha256 for file hashes; others would suffice,
    # but sha256 has less collisions so is a little bit safer
    sha256 = models.CharField(max_length=64, null=True, blank=True)

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
    def _main_path(self):
        return self.path

    @property
    def name(self):
        return self._parent_object.name

    def save(self, *args, **kwargs):
        to_update = False
        if not self.sha256:
            # if the hash has never been calc'd, we know this is a
            # new record and we need to update the metadata file,
            # and we of course know we need to hash the file
            to_update = True
            self.sha256 = hash_file(self._main_path)

        return super(FileData, self).save(*args, to_update=to_update, **kwargs)

    @classmethod
    @transaction.atomic
    def create(cls, input_file, File, id=None, comment=""):
        if not id:
            id = generate_uuid(cls)

        now = timezone.now()
        ext = os.path.splitext(os.path.basename(input_file))[1]
        path = os.path.join(File.parent_directory,
                            str(id) + ext)
        shutil.copy(input_file, path)

        try:
            data_obj = cls(aoi=File.aoi,
                           _parent_object=File,
                           path=path,
                           created_by=File.created_by,
                           created_at=now,
                           id=id,
                           comment=comment)
            data_obj.save()
        except:
            try:
                os.remove(path)
            except:
                exception("Failed to remove File Data on create error.")
            raise
        else:
            return data_obj

    def export(self, output_dir, name=None, copy_function=shutil.copy):
        if not name:
            name = self.name
        copy_function(self._main_path, os.path.join(output_dir, name))


class LayerData(FileData):
    #ext = ""

    class Meta:
        proxy = True

    #@property
    #def _main_path(self):
    #    return self.path + self.ext

    @classmethod
    @transaction.atomic
    def create(cls, arcpy_ext_layer, File, id=None, comment=""):
        if not id:
            id = generate_uuid(cls)

        now = timezone.now()
        output_dir = File.parent_directory
        newlyr = arcpy_ext_layer.copy_to_file(output_dir,
                                              outname=sanitize_uuid(str(id)))

        try:
            data_obj = cls(aoi=File.aoi,
                           _parent_object=File,
                           path=newlyr.path,
                           created_by=File.created_by,
                           created_at=now,
                           id=id,
                           comment=comment)
            data_obj.save()
        except:
            try:
                from arcpy.management import Delete
                Delete(newlyr.path)
            except:
                exception("Failed to remove File Data on create error.")
            raise
        else:
            return data_obj


class VectorData(LayerData):
    #ext = constants.FC_EXT

    class Meta:
        proxy = True

    def export(self, output_dir, name=None):
        from arcpy.management import CopyFeatures
        super(VectorData, self).export(output_dir, name, CopyFeatures)


class RasterData(LayerData):
    #ext = constants.RASTER_EXT

    class Meta:
        proxy = True

    def export(self, output_dir, name=None):
        from arcpy.management import CopyRaster
        super(RasterData, self).export(output_dir, name, CopyRaster)


class TableData(LayerData):
    #ext = constants.TABLE_EXT

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
