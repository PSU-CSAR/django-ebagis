from __future__ import absolute_import

from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models.pourpoint import PourPoint


class PourPointSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = PourPoint
        geo_field = 'location'
        fields = ('name', 'awdb_id')
