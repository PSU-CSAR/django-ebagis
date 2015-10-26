from __future__ import absolute_import

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

# model objects
from ..models.aoi import AOI

# serializers
from ..serializers.aoi import (
    AOIListSerializer, AOIGeoListSerializer, AOISerializer, AOIGeoSerializer,
)

# customer renderers
from ..renderers import GeoJSONRenderer

# custom mixins
from .mixins import (
    UploadMixin, UpdateMixin, DownloadMixin, MultiSerializerMixin,
)


class AOIViewSet(UploadMixin, UpdateMixin, DownloadMixin,
                 MultiSerializerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows AOIs to be viewed or edited.
    """
    queryset = AOI.objects.all()
    serializers = {
        'default': AOISerializer,
        'list': AOIListSerializer,
    }
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, GeoJSONRenderer)
    parser_classes = (
        JSONParser,
        FormParser,
        MultiPartParser,
    )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if request.accepted_renderer.format == 'geojson':
            serializer = AOIGeoListSerializer(queryset, many=True,
                                              context={'request': request})
        else:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.accepted_renderer.format == 'geojson':
            serializer = AOIGeoSerializer(instance,
                                          context={'request': request}
                                          )
        else:
            serializer = self.get_serializer(instance)
        return Response(serializer.data)
