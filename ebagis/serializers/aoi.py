from __future__ import absolute_import

from django.core.urlresolvers import NoReverseMatch
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models.aoi import AOI

from .user import UserSerializer
from .geodatabase import (
    SurfacesSerializer, LayersSerializer, AOIdbSerializer, AnalysisSerializer,
    PrismDirSerializer
)


class AOIListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='aoi-detail',
                                               read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = AOI
        fields = ('url', 'name', 'created_at', 'created_by', "comment")


class AOIGeoListSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = AOI
        geo_field = 'boundary'
        fields = ('url', 'name')


class AOISerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='aoi-detail',
                                               read_only=True)
    created_by = UserSerializer(read_only=True)
    surfaces = SurfacesSerializer(read_only=True)
    layers = LayersSerializer(read_only=True)
    aoidb = AOIdbSerializer(read_only=True)
    analysis = AnalysisSerializer(read_only=True)
    prism = PrismDirSerializer(read_only=True)
    #maps = MapDocSerializer(read_only=True, many=True)
    #hruzones = HRUZonesSerializer(read_only=True, many=True)
    parent_aoi = AOIListSerializer(read_only=True)
    child_aois = AOIListSerializer(read_only=True)

    class Meta:
        model = AOI
        fields = ("url", "name", "created_by", "created_at", "comment",
                  "surfaces", "layers", "aoidb", "analysis", "prism",
                  #"maps",
                  #"hruzones",
                  parent_aoi, child_aois,
                  )


class AOIGeoSerializer(GeoFeatureModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='aoi-detail',
                                               read_only=True)
    created_by = UserSerializer(read_only=True)
    surfaces = SurfacesSerializer(read_only=True)
    layers = LayersSerializer(read_only=True)
    aoidb = AOIdbSerializer(read_only=True)
    analysis = AnalysisSerializer(read_only=True)
    prism = PrismDirSerializer(read_only=True)
    #maps = MapDocSerializer(read_only=True, many=True)
    #hruzones = HRUZonesSerializer(read_only=True, many=True)
    parent_aoi = AOIListSerializer(read_only=True)
    child_aois = AOIListSerializer(read_only=True)

    class Meta:
        model = AOI
        geo_field = 'boundary'
