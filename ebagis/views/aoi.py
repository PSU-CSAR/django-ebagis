from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

# custom mixins
from .mixins import MultiSerializerViewSet

# model objects
from ..models.aoi import AOI

# serializers
from ..serializers.aoi import (
    AOIListSerializer, AOIGeoListSerializer, AOISerializer, AOIGeoSerializer,
)
from ..serializers.geodatabase import (
    SurfacesSerializer, LayersSerializer, AOIdbSerializer, AnalysisSerializer,
    PrismDirSerializer
)

# customer renderers
from ..renderers import GeoJSONRenderer

# up- and down-load views
from .upload import UploadView
from .download import DownloadViewSet


class AOIViewSet(MultiSerializerViewSet):
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

    def create(self, request, *args, **kwargs):
        return UploadView.new_upload(AOI, request)

    @detail_route()
    def surfaces(self, request, *args, **kwargs):
        surfaces = self.get_object().surfaces
        serializer = SurfacesSerializer(surfaces, context={'request': request})
        return Response(serializer.data)

    @detail_route()
    def layers(self, request, *args, **kwargs):
        layers = self.get_object().layers
        serializer = LayersSerializer(layers, context={'request': request})
        return Response(serializer.data)

    @detail_route()
    def aoidb(self, request, *args, **kwargs):
        aoidb = self.get_object().aoidb
        serializer = AOIdbSerializer(aoidb, context={'request': request})
        return Response(serializer.data)

    @detail_route()
    def analysis(self, request, *args, **kwargs):
        analysis = self.get_object().analysis
        serializer = AnalysisSerializer(analysis, context={'request': request})
        return Response(serializer.data)

    @detail_route()
    def prism(self, request, *args, **kwargs):
        prism = self.get_object().prism
        serializer = PrismDirSerializer(prism, context={'request': request})
        return Response(serializer.data)

    @detail_route()
    def download(self, request, *args, **kwargs):
        aoi = self.get_object()
        return DownloadViewSet.new_download(aoi, request)
