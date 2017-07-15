from __future__ import absolute_import

from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

from ...renderers import GeoJSONRenderer

from ..models.pourpoint import PourPoint

from ..serializers.pourpoint import (
    PourPointSerializer, PourPointBoundarySerializer
)
from ..serializers.aoi import AOIListSerializer


@permission_classes((AllowAny, ))
class PourPointViewSet(viewsets.ModelViewSet):
    serializer_class = PourPointSerializer
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, GeoJSONRenderer)

    def get_queryset(self):
        if self.request.query_params.get('all', False) or \
                self.kwargs.get('pk', None):
            return PourPoint.objects.all()
        # unless explicitly specified, we only want to
        # show pourpoints with an associated AOI record
        return PourPoint.objects.filter(aois__isnull=False).distinct()

    def aois(self, request, *args, **kwargs):
        object = self.get_object()
        serializer = AOIListSerializer(
            object.aois,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)


@permission_classes((AllowAny, ))
class PourPointBoundaryViewSet(viewsets.ModelViewSet):
    serializer_class = PourPointBoundarySerializer
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, GeoJSONRenderer)

    def get_queryset(self):
        if self.request.query_params.get('all', False) or \
                self.kwargs.get('pk', None):
            return PourPoint.objects.all()
        # unless explicitly specified, we only want to
        # show pourpoints with an associated AOI record
        return PourPoint.objects.filter(aois__isnull=False).distinct()

    def aois(self, request, *args, **kwargs):
        object = self.get_object()
        serializer = AOIListSerializer(
            object.aois,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)
