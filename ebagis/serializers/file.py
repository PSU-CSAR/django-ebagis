from __future__ import absolute_import

from rest_framework import serializers

from ..models.file import File, XML, Raster, Vector, Table, MapDocument

from .file_data import (
    FileDataSerializer, XMLDataSerializer, VectorDataSerializer,
    RasterDataSerializer, TableDataSerializer,
)


class FileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    versions = FileDataSerializer(read_only=True, many=True)

    def get_url(self, obj):
        return obj.get_url(self.context['request'])

    class Meta:
        model = File


class XMLSerializer(FileSerializer):
    versions = XMLDataSerializer(read_only=True, many=True)

    class Meta:
        model = XML


class VectorSerializer(FileSerializer):
    versions = VectorDataSerializer(read_only=True, many=True)

    class Meta:
        model = Vector


class RasterSerializer(FileSerializer):
    versions = RasterDataSerializer(read_only=True, many=True)

    class Meta:
        model = Raster


class TableSerializer(FileSerializer):
    versions = TableDataSerializer(read_only=True, many=True)

    class Meta:
        model = Table


class MapDocumentSerializer(FileSerializer):
    versions = MapDocumentDataSerializer(read_only=True, many=True)

#    def get_url(self, obj):
#        return reverse(obj.content_object.name.lower() + '-' +
#                       type(obj).__name__.lower() + '-detail',
#                       kwargs={"aoi_pk": obj.content_object.aoi_id,
#                               "pk": obj.id},
#                       request=self.context['request'])

    class Meta:
        model = MapDocument
