from __future__ import absolute_import

from rest_framework import serializers

from ..models.geodatabase import (
    Surfaces, Layers, Prism, AOIdb, HRUZonesGDB, Analysis, Geodatabase,
)
from ..models.zones import HRUZones
from ..models.directory import PrismDir

from ..constants import MULTIPLE_GDBS

from .file import (
    RasterSerializer, VectorSerializer, TableSerializer, XMLSerializer,
)


class GeodatabaseSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    rasters = RasterSerializer(read_only=True, many=True)
    vectors = VectorSerializer(read_only=True, many=True)
    tables = TableSerializer(read_only=True, many=True)
    xmls = XMLSerializer(read_only=True, many=True)

    def get_url(self, obj):
        return obj.get_url(self.context['request'])

    class Meta:
        model = Geodatabase


class SurfacesSerializer(GeodatabaseSerializer):
    class Meta:
        model = Surfaces


class LayersSerializer(GeodatabaseSerializer):
    class Meta:
        model = Layers


class PrismSerializer(GeodatabaseSerializer):
    def get_url(self, obj):
        return obj.get_url(self.context['request'])

    class Meta:
        model = Prism


class AOIdbSerializer(GeodatabaseSerializer):
    class Meta:
        model = AOIdb


class AnalysisSerializer(GeodatabaseSerializer):
    class Meta:
        model = Analysis


class HRUZonesSerializer(GeodatabaseSerializer):
    class Meta:
        model = HRUZones


class PrismDirSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    versions = PrismSerializer(read_only=True, many=True)

    def get_url(self, obj):
        return obj.get_url(self.context['request'])

    class Meta:
        model = PrismDir
