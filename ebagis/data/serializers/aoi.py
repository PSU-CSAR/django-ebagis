from __future__ import absolute_import

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ebagis.serializers.user import UserSerializer

from ..models.aoi import AOI

from .data import (
    GeodatabaseSerializer, HRUZonesSerializer, MapsSerializer
)


class AOIListSerializer(serializers.HyperlinkedModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = AOI
        fields = ('id', 'url', 'name', 'created_at', 'created_by', "comment")
        extra_kwargs = {'url': {'view_name': 'aoi-base:detail'}}


class AOIGeoListSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = AOI
        geo_field = 'boundary'
        fields = ('id', 'url', 'name')
        extra_kwargs = {'url': {'view_name': 'aoi-base:detail'}}


class AOISerializer(serializers.HyperlinkedModelSerializer):
    created_by = UserSerializer(read_only=True)
    surfaces = serializers.SerializerMethodField()
    layers = serializers.SerializerMethodField()
    aoidb = serializers.SerializerMethodField()
    analysis = serializers.SerializerMethodField()
    prisms = serializers.SerializerMethodField()
    maps = serializers.SerializerMethodField()
    zones = serializers.SerializerMethodField()
    parent_aoi = AOIListSerializer(read_only=True)
    child_aois = AOIListSerializer(read_only=True, many=True)
    pourpoint = serializers.HyperlinkedRelatedField(
        view_name='pourpoint-base:detail',
        read_only=True,
    )

    def _get_object(self, obj, obj_to_serialize, serializer):
        return serializer(
            obj_to_serialize,
            context={'request': self.context['request']}
        ).data

    def _get_geodatabase(self, obj, geodatabase):
        return self._get_object(obj, geodatabase, GeodatabaseSerializer)

    def get_surfaces(self, obj):
        return self._get_geodatabase(obj, obj.contents.surfaces)

    def get_layers(self, obj):
        return self._get_geodatabase(obj, obj.contents.layers)

    def get_aoidb(self, obj):
        return self._get_geodatabase(obj, obj.contents.aoidb)

    def get_analysis(self, obj):
        return self._get_geodatabase(obj, obj.contents.analysis)

    def get_prisms(self, obj):
        return [self._get_geodatabase(obj, prism)
                for prism in obj.contents.prism]

    def get_maps(self, obj):
        return self._get_object(obj, obj.contents.maps, MapsSerializer)

    def get_zones(self, obj):
        return [self._get_object(obj, zone, HRUZonesSerializer)
                for zone in obj.contents.zones]

    class Meta:
        model = AOI
        fields = ('id', 'url', 'name', 'created_by', 'created_at', 'comment',
                  'surfaces', 'layers', 'aoidb', 'analysis', 'prisms',
                  'maps',
                  'zones',
                  'parent_aoi', 'child_aois',
                  'modified_at',
                  'pourpoint',
                  )
        extra_kwargs = {'url': {'view_name': 'aoi-base:detail'}}


class AOIGeoSerializer(GeoFeatureModelSerializer, AOISerializer):
    class Meta:
        model = AOI
        geo_field = 'boundary'
        fields = ('id', 'url', 'name', 'created_by', 'created_at', 'comment',
                  'surfaces', 'layers', 'aoidb', 'analysis', 'prisms',
                  'maps',
                  'zones',
                  'parent_aoi', 'child_aois',
                  'modified_at',
                  'pourpoint',
                  )
        extra_kwargs = {'url': {'view_name': 'aoi-base:detail'}}
