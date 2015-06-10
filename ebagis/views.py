import logging

from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType

from rest_framework import viewsets, views
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.parsers import FileUploadParser, JSONParser, FormParser,\
    MultiPartParser

from rest_framework import mixins
from rest_framework import generics

from drf_chunked_upload.views import ChunkedUploadView

from djcelery.models import TaskMeta

# model objects
from django.contrib.auth.models import User, Group, Permission
from .models import AOI, Surfaces, Layers, AOIdb, Prism, HRUZones, XML,\
    Vector, Raster, Table, MapDocument, Analysis, Geodatabase,\
    AOIUpload, UpdateUpload, Download, PrismDir

# serializers
from .serializers import AOISerializer, SurfacesSerializer, LayersSerializer,\
    PrismSerializer, AOIdbSerializer, HRUZonesSerializer, XMLSerializer,\
    VectorSerializer, RasterSerializer, TableSerializer, MapDocSerializer,\
    UserSerializer, GroupSerializer, AnalysisSerializer, AOIListSerializer,\
    AOIGeoListSerializer, GeodatabaseSerializer, AOIGeoSerializer,\
    AOIUploadSerializer, UpdateUploadSerializer, PermissionSerializer,\
    DownloadSerializer, PrismDirSerializer


from .tasks import add_aoi, export_data
from .constants import URL_FILTER_QUERY_ARG_PREFIX


#geodatabases = {
#    'surfaces': {'model': Surfaces, 'serializers': SurfacesSerializer},
#    'layers': {'model': Layers, 'serializer': LayersSerializer},
#    'analysis': {'model': Analysis, 'serializer': AnalysisSerializer},
#    'aoi': {'model': AOIdb, 'serializer': AOIdbSerializer},
#    'prism': {'model': Prism, 'serializer': PrismSerializer},
#}


class GeoJSONRenderer(JSONRenderer):
    format = "geojson"


class MultiSerializerViewSet(viewsets.ModelViewSet):
    """Allows multiple serializers to be defined for a ModelViewSet.

    Use like:

        class SomeViewSet(MultiSerializerViewSet):
        model = models.SomeModel

        serializers = {
            'default': serializers.SomeModelSerializer
            'list':    serializers.SomeModelListSerializer,
            'detail':  serializers.SomeModelDetailSerializer,
            # etc.
        }
    """
    serializers = {
        'default': None,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action,
                                    self.serializers['default'])


class APIRoot(APIView):
    def get(self, request):
        return Response({
            'AOIs': reverse('aoi-list', request=request),
            'AOI Uploads': reverse('aoiupload-list', request=request),
            'Downloads': reverse('download-list', request=request),
            'Users': reverse('user-list', request=request),
            'Groups': reverse('group-list', request=request),
        })


class DownloadViewSet(viewsets.ModelViewSet):
    queryset = Download.objects.all()
    serializer_class = DownloadSerializer

    def retrieve(self, request, *args, **kwargs):
        import os

        instance = self.get_object()

        if instance.file:
            response = HttpResponse(instance.file,
                                    content_type='application/zip')
            name = os.path.basename(instance.file.file.name)
            response['Content-Disposition'] = \
                'attachment; filename="' + name + '"'
            return response

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def download(self, request, content_type, object_id):
        download = Download(user=request.user,
                            content_type=content_type,
                            object_id=object_id)
        download.save()
        result = export_data.delay(download.id)
        download.task, created = \
            TaskMeta.objects.get_or_create(task_id=result.task_id)
        download.save()
        serializer = self.serializer_class(download,
                                           context={'request': request})
        return Response(serializer.data)


class AOIUploadView(ChunkedUploadView):
    model = AOIUpload
    serializer_class = AOIUploadSerializer

    def on_completion(self, upload, request):
        result = add_aoi.delay(upload.id)
        upload.task, created = \
            TaskMeta.objects.get_or_create(task_id=result.task_id)
        upload.save()


class UpdateUploadView(ChunkedUploadView):
    model = UpdateUpload
    serializer_class = UpdateUploadSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


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
        logging.info(request.data)
        upload_view = AOIUploadView()
        if request.method == 'PUT':
            return upload_view.put(request)
        elif request.method == 'POST':
            return upload_view.post(request)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        download_view = DownloadViewSet()
        if request.method == 'GET':
            return download_view.download(
                request,
                ContentType.objects.get_for_model(aoi.__class__),
                aoi.id
            )
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PrismViewSet(viewsets.ModelViewSet):
    serializer_class = PrismSerializer

    def get_queryset(self):
        query_dict = get_queryset_arguments(self)
        print query_dict
        return PrismDir.objects.get(**query_dict).versions


class HRUZonesViewSet(viewsets.ModelViewSet):
    serializer_class = HRUZonesSerializer

    def get_queryset(self):
        query_dict = get_queryset_arguments(self)
        return HRUZones.objects.get(**query_dict)


class GeodatabaseXMLViewSet(viewsets.ModelViewSet):
    serializer_class = XMLSerializer

    def get_queryset(self):
        query_dict = get_queryset_arguments(self)
        return Geodatabase.objects.get(**query_dict).xmls.all()


class GeodatabaseTableViewSet(viewsets.ModelViewSet):
    serializer_class = TableSerializer

    def get_queryset(self):
        query_dict = get_queryset_arguments(self)
        return Geodatabase.objects.get(**query_dict).tables.all()


class GeodatabaseVectorViewSet(viewsets.ModelViewSet):
    serializer_class = VectorSerializer

    def get_queryset(self):
        query_dict = get_queryset_arguments(self)
        return Geodatabase.objects.get(**query_dict).vectors.all()


class GeodatabaseRasterViewSet(viewsets.ModelViewSet):
    serializer_class = RasterSerializer

    def get_queryset(self):
        query_dict = get_queryset_arguments(self)
        return Geodatabase.objects.get(**query_dict).rasters.all()


#class AOIList(mixins.ListModelMixin,
#              generics.GenericAPIView):
#    queryset = AOI.objects.all()
#    serializer_class = AOISerializer
#
#    def get(self, request, *args, **kwargs):
#        return self.list(request, *args, **kwargs)
#
#    def post(self, request, *args, **kwargs):
#        return Response({"message": "Not implemented. Try again tomorrow!"})
#
#
#class AOIDetail(mixins.RetrieveModelMixin,
#                mixins.UpdateModelMixin,
#                mixins.DestroyModelMixin,
#                generics.GenericAPIView):
#    queryset = AOI.objects.all()
#    serializer_class = AOISerializer
#
#    def get(self, request, *args, **kwargs):
#        return self.retrieve(request, *args, **kwargs)
#
#    def put(self, request, *args, **kwargs):
#        return self.update(request, *args, **kwargs)
#
#    def delete(self, request, *args, **kwargs):
#        return self.destroy(request, *args, **kwargs)


# *************** BASE FILE VIEWSETS ***************
#
#class XMLViewSet(viewsets.ModelViewSet):
#    """
#    API endpoint that allows XMLs to be viewed or edited.
#    """
#    queryset = XML.objects.all()
#    serializer_class = XMLSerializer
#
#
#class VectorViewSet(viewsets.ModelViewSet):
#    """
#    API endpoint that allows Vectors to be viewed or edited.
#    """
#    queryset = Vector.objects.all()
#    serializer_class = VectorSerializer
#
#
#class RasterViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
#    """
#    API endpoint that allows Rasters to be viewed or edited.
#    """
#    queryset = Raster.objects.all()
#    serializer_class = RasterSerializer
#
#
#class TableViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
#    """
#    API endpoint that allows Tables to be viewed or edited.
#    """
#    queryset = Table.objects.all()
#    serializer_class = TableSerializer
#
#
#class MapDocViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
#    """
#    API endpoint that allows Map Documents to be viewed or edited.
#    """
#    queryset = MapDocument.objects.all()
#    serializer_class = MapDocSerializer


# *************** UTILITY FUNCTIONS ***************

def get_queryset_arguments(obj):
    query_dict = {}

    for kwarg in obj.kwargs:
        if kwarg.startswith(URL_FILTER_QUERY_ARG_PREFIX):
            query_lookup = kwarg.replace(
                URL_FILTER_QUERY_ARG_PREFIX,
                '',
                1
            )
            query_value = obj.kwargs.get(kwarg)
            query_dict[query_lookup] = query_value

    return query_dict
