from __future__ import absolute_import

from django.contrib.contenttypes.models import ContentType

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


from .upload import UploadView
from .mixins import (
    UpdateMixin, DownloadMixin, MultiSerializerMixin,
)


class AOIViewSet(UpdateMixin, DownloadMixin, MultiSerializerMixin,
                 viewsets.ModelViewSet):
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

    def create(self, request, *args, **kwargs):
        # if the user supplied a parent id for an AOI upload, we know
        # that it also must be an AOI instance and we can assign the
        # the parent content type for the user
        if hasattr(request.data, "parent_object_id"):
            request.data["parent_content_type"] = \
                ContentType.objects.get_for_model(AOI).pk
        return UploadView.new_upload(self.queryset.model, request)

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
