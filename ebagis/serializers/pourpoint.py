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
        use_boundary = self.context['request'].GET.get('boundary', False)
        return obj.boundary if use_boundary else obj.location

    class Meta:
        model = PourPoint
        geo_field = 'geometry'
        fields = ('name', 'awdb_id', 'aois')
