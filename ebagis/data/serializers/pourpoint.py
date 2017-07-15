from __future__ import absolute_import

from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeometrySerializerMethodField,
)

from .aoi import AOIListSerializer
from ..models.pourpoint import PourPoint


class PourPointSerializer(GeoFeatureModelSerializer):
    geometry = GeometrySerializerMethodField()
    aois = AOIListSerializer(read_only=True, many=True)

    def get_geometry(self, obj):
        use_boundary = self.context['request'].query_params.get(
            'boundary', False
        )
        use_simplified = self.context['request'].query_params.get(
            'simplified', True
        )
        if use_boundary and use_simplified:
            return obj.boundary_simple
        elif use_boundary:
            return obj.boundary
        else:
            return obj.location

    class Meta:
        model = PourPoint
        geo_field = 'geometry'
        fields = ('id', 'name', 'awdb_id', 'source', 'aois')


class PourPointBoundarySerializer(GeoFeatureModelSerializer):
    aois = AOIListSerializer(read_only=True, many=True)
    boundary = GeometrySerializerMethodField()

    def get_boundary(self, obj):
        use_simplified = self.context['request'].query_params.get(
            'simplified', True
        )
        return obj.boundary_simple if use_simplified else obj.boundar

    class Meta:
        model = PourPoint
        geo_field = 'boundary'
        fields = ('id', 'name', 'awdb_id', 'source', 'aois')
