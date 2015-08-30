from rest_framework import viewsets

# model objects
from ..models.zones import HRUZones
from ..models.directory import PrismDir

# serializers
from ..serializers.geodatabase import (
    HRUZonesSerializer, PrismSerializer,
)

# utility functions
from ..utilities import get_queryset_arguments


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

