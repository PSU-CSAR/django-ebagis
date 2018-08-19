from __future__ import absolute_import

import numpy.ma as ma

from django.contrib.gis.gdal import SpatialReference

from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework_gis.serializers import GeometryField

from ..models import PRISMRaster

from ..utils.gis.raster.clip import extend_raster


class BoundSerializer(serializers.Serializer):
    boundary = GeometryField()


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def PRISMStatsView(request):
    if request.method == "POST":
        serializer = BoundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        study_area = serializer.validated_data['boundary'].ogr
        study_area.srs = SpatialReference(4326)

        raster = PRISMRaster.objects.all()[0].raster
        extend_raster(raster)

        clipped = raster.clip(study_area)
        clipped.mask(study_area, all_touched=True)
        clipped.warp({'driver': 'GTiff', 'name': 'clipped.tif'})
        data = ma.masked_values(
            clipped.bands[0].data(),
            clipped.bands[0].nodata_value,
        )
        return Response({
            'min': data.min(),
            'max': data.max(),
            'mean': data.mean(),
        })
