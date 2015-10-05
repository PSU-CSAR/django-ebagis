from rest_framework import viewsets

from ..models.zones import HRUZones
from ..models.directory import PrismDir

from ..serializers.geodatabase import (
    HRUZonesSerializer, PrismSerializer,
)

from .mixins import UploadMixin, UpdateMixin, DownloadMixin


class PrismViewSet(UploadMixin, UpdateMixin, DownloadMixin,
                   viewsets.ModelViewSet):
    serializer_class = PrismSerializer

    def get_queryset(self):
        filter = {}

        if "aoi_id" in self.kwargs:
            filter["aoi_id"] = self.kwargs["aoi_id"]

        return PrismDir.objects.get(**filter).versions


class HRUZonesViewSet(UploadMixin, UpdateMixin, DownloadMixin,
                      viewsets.ModelViewSet):
    serializer_class = HRUZonesSerializer

    def get_queryset(self):
        filter = {}

        if "aoi_id" in self.kwargs:
            filter["aoi_id"] = self.kwargs["aoi_id"]

        return HRUZones.objects.get(**filter)

