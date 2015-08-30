from rest_framework import viewsets

# model objects
from ..models.geodatabase import Geodatabase

# serializers
from ..serializers.file import (
    RasterSerializer, VectorSerializer, TableSerializer, XMLSerializer,
    MapDocSerializer
)

# other
from ..utilties import get_queryset_arguments


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

