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

from .base import RandomPrimaryIdModel
from .mixins import (
    ProxyMixin, DateMixin, NameMixin, CreatedByMixin, AOIRelationMixin,
    )


class FileData(ProxyMixin, DateMixin, NameMixin, CreatedByMixin,
               AOIRelationMixin, RandomPrimaryIdModel):
    path = models.CharField(max_length=1024, unique=True)
    encoding = models.CharField(max_length=20, null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=10)
    content_object = GenericForeignKey('content_type', 'object_id')

    # TODO Finish this method and those for the sub classes
    # TODO Review all other class create methods -- finish GDB methods
    @classmethod
    @transaction.atomic
    def create(cls, input_file, File, user):
        content_type = ContentType.objects.get_for_model(
            File.__class__,
            for_concrete_model=False
        )

        now = timezone.now()
        name, ext = os.path.splitext(os.path.basename(input_file))
        path = os.path.join(File.content_object.path,
                            name + now.strftime("_%Y%m%d%H%M%S") + ext)
        shutil.copy(input_file, path)

        try:
            data_obj = cls(aoi=File.aoi,
                           content_type=content_type,
                           object_id=File.id,
                           path=path,
                           name=name+ext,
                           created_by=user,
                           created_at=now)
            data_obj.save()
        except:
            try:
                os.remove(path)
            except:
                exception("Failed to remove File Data on create error.")
            raise
        return data_obj

    def export(self, output_dir):
        shutil.copy(self.path, os.path.join(output_dir, self.name))

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
    def create(cls, arcpy_ext_layer, File, user):
        content_type = ContentType.objects.get_for_model(
            File.__class__,
            for_concrete_model=False
        )

        now = timezone.now()
        output_dir = File.content_object.path
        output_name = arcpy_ext_layer.name + now.strftime("_%Y%m%d%H%M%S")
        newlyr = arcpy_ext_layer.copy_to_file(output_dir, outname=output_name)

        print cls

        try:
            data_obj = cls(aoi=File.aoi,
                           content_type=content_type,
                           object_id=File.id,
                           path=newlyr.path,
                           name=arcpy_ext_layer.name,
                           created_by=user,
                           created_at=now)
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

    def export(self, output_dir):
        from arcpy.management import CopyFeatures
        CopyFeatures(self.path, os.path.join(output_dir, self.name))

VectorData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'vector'}


class RasterData(LayerData):
    #srs_wkt = models.CharField(max_length=1000)
    #resolution = models.FloatField()

    class Meta:
        proxy = True

    def export(self, output_dir):
        from arcpy.management import CopyRaster
        CopyRaster(self.path, os.path.join(output_dir, self.name))

RasterData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'raster'}


class TableData(LayerData):
    class Meta:
        proxy = True

    def export(self, output_dir):
        from arcpy.management import CopyRows
        CopyRows(self.path, os.path.join(output_dir, self.name))

TableData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'table'}


# used in the Layer class to find the proper data class to go
# with a given layer data type
LAYER_DATA_CLASSES = {
    constants.FC_TYPECODE: VectorData,
    constants.RASTER_TYPECODE: RasterData,
    constants.TABLE_TYPECODE: TableData,
}
