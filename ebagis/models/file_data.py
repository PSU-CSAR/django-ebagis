from __future__ import absolute_import
import os
import shutil
from logging import exception

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.gis.db import models
from django.db import transaction

from .. import constants
from ..utils.validation import hash_file, generate_uuid, sanitize_uuid

from .base import ABC
from .mixins import (
    ProxyMixin, DateMixin, CreatedByMixin, AOIRelationMixin,
)


class FileData(ProxyMixin, DateMixin, CreatedByMixin,
               AOIRelationMixin, ABC):
    path = models.CharField(max_length=1024, unique=True)
    encoding = models.CharField(max_length=20, null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    # we are using sha256 for file hashes; others would suffice,
    # but sha256 has less collisions so is a little bit safer
    sha256 = models.CharField(max_length=64, null=True, blank=True)

    # lists of field names to be written to the XML metadata file
    # we only need those that cannot be recreated, though
    # the hash of the file is included as it might prove
    # useful for version detection later on
    _archive_fields = {
        "read_only": ["id", "created_at", "created_by", "sha256", "object_id"],
        "writable": ["comment"]
    }

    class Meta:
        index_together = [
            ["object_id", "content_type", "classname"],
        ]

    @property
    def _main_path(self):
        return self.path

    @property
    def name(self):
        return self.content_object.name

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
    def create(cls, input_file, File, user, id=None, comment=""):
        content_type = ContentType.objects.get_for_model(
            File.__class__,
            for_concrete_model=False,
        )

        if not id:
            id = generate_uuid(cls)

        now = timezone.now()
        ext = os.path.splitext(os.path.basename(input_file))[1]
        path = os.path.join(File.path,
                            str(id) + ext)
        shutil.copy(input_file, path)

        try:
            data_obj = cls(aoi=File.aoi,
                           content_type=content_type,
                           object_id=File.id,
                           path=path,
                           created_by=user,
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
        return data_obj

    def export(self, output_dir, name=None, copy_function=shutil.copy):
        if not name:
            name = self.name
        copy_function(self._main_path, os.path.join(output_dir, name))

# "Data" types must match their enclosing layer type, e.g., a vector
# data instance can only relate to a vector layer instance. Thus,
# each type needs to have the content type choices limited to
# restrict allowable relations to the appropriate class.
FileData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'file'}


class XMLData(FileData):
    class Meta:
        proxy = True

XMLData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'xml'}


class MapDocumentData(FileData):
    class Meta:
        proxy = True

MapDocumentData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'mapdocument'}


class LayerData(FileData):
    class Meta:
        proxy = True

    @classmethod
    @transaction.atomic
    def create(cls, arcpy_ext_layer, File, user, id=None, comment=""):
        content_type = ContentType.objects.get_for_model(
            File.__class__,
            for_concrete_model=False
        )

        if not id:
            id = generate_uuid(cls)

        now = timezone.now()
        output_dir = File.path
        # the following line is dead now that IDs are used for file names,
        # but I want to keep it around for reference in case I need later
        #output_name = arcpy_ext_layer.name + now.strftime("_%Y%m%d%H%M%S")
        newlyr = arcpy_ext_layer.copy_to_file(output_dir,
                                              outname=sanitize_uuid(str(id)))

        try:
            data_obj = cls(aoi=File.aoi,
                           content_type=content_type,
                           object_id=File.id,
                           path=os.path.splitext(newlyr.path)[0],
                           created_by=user,
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
        return data_obj


class VectorData(LayerData):
#    srs_wkt = models.CharField(max_length=1000)
#    geom_type = models.CharField(max_length=50)

    class Meta:
        proxy = True

    @property
    def _main_path(self):
        return self.path + constants.FC_EXT

    def export(self, output_dir, name=None):
        from arcpy.management import CopyFeatures
        super(VectorData, self).export(output_dir, name, CopyFeatures)

VectorData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'vector'}


class RasterData(LayerData):
    #srs_wkt = models.CharField(max_length=1000)
    #resolution = models.FloatField()

    class Meta:
        proxy = True

    @property
    def _main_path(self):
        return self.path + constants.RASTER_EXT

    def export(self, output_dir, name=None):
        from arcpy.management import CopyRaster
        super(RasterData, self).export(output_dir, name, CopyRaster)

RasterData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'raster'}


class TableData(LayerData):
    class Meta:
        proxy = True

    @property
    def _main_path(self):
        return self.path + constants.TABLE_EXT

    def export(self, output_dir, name=None):
        from arcpy.management import CopyRows
        super(TableData, self).export(output_dir, name, CopyRows)

TableData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'table'}


# used in the Layer class to find the proper data class to go
# with a given layer data type
LAYER_DATA_CLASSES = {
    constants.FC_TYPECODE: VectorData,
    constants.RASTER_TYPECODE: RasterData,
    constants.TABLE_TYPECODE: TableData,
}
