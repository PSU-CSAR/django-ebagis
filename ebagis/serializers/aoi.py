from __future__ import absolute_import

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models.aoi import AOI

from .user import UserSerializer
from .data import (
    GeodatabaseSerializer, FileSerializer, HRUZonesSerializer,
    PrismDirSerializer,
)


class AOIListSerializer(serializers.HyperlinkedModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = AOI
        fields = ('url', 'name', 'created_at', 'created_by', "comment")
        extra_kwargs = {'url': {'view_name': 'aoi-base:detail'}}


class AOIGeoListSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = AOI
        geo_field = 'boundary'
        fields = ('url', 'name')
        extra_kwargs = {'url': {'view_name': 'aoi-base:detail'}}


class AOISerializer(serializers.HyperlinkedModelSerializer):
    created_by = UserSerializer(read_only=True)
    surfaces = GeodatabaseSerializer(read_only=True)
    layers = GeodatabaseSerializer(read_only=True)
    aoidb = GeodatabaseSerializer(read_only=True)
    analysis = GeodatabaseSerializer(read_only=True)
    prism = GeodatabaseSerializer(read_only=True, many=True)
    maps = FileSerializer(read_only=True, many=True)
    zones = HRUZonesSerializer(read_only=True, many=True)
    parent_aoi = AOIListSerializer(read_only=True)
    child_aois = AOIListSerializer(read_only=True, many=True)

    class Meta:
        model = AOI
        fields = ("url", "name", "created_by", "created_at", "comment",
                  "surfaces", "layers", "aoidb", "analysis", "prism",
                  "maps",
                  "zones",
                  "parent_aoi", "child_aois",
                  "modified_at",
                  )
        extra_kwargs = {'url': {'view_name': 'aoi-base:detail'}}


class AOIGeoSerializer(GeoFeatureModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='aoi:detail',
                                               read_only=True)
    created_by = UserSerializer(read_only=True)
    surfaces = GeodatabaseSerializer(read_only=True)
    layers = GeodatabaseSerializer(read_only=True)
    aoidb = GeodatabaseSerializer(read_only=True)
    analysis = GeodatabaseSerializer(read_only=True)
    prism = GeodatabaseSerializer(read_only=True, many=True)
    maps = FileSerializer(read_only=True, many=True)
    zones = HRUZonesSerializer(read_only=True, many=True)
    parent_aoi = AOIListSerializer(read_only=True)
    child_aois = AOIListSerializer(read_only=True, many=True)

    class Meta:
        model = AOI
        geo_field = 'boundary'
