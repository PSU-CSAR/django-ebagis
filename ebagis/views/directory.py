from ..models.zones import HRUZones, HRUZonesData
from ..models.directory import PrismDir

from ..serializers.data import (
    HRUZonesSerializer, HRUZonesDataSerializer, PrismDirSerializer,
)

from .base import BaseViewSet
from .mixins import UploadMixin, UpdateMixin, DownloadMixin


class PrismViewSet(UploadMixin, UpdateMixin, DownloadMixin,
                   BaseViewSet):
    serializer_class = PrismDirSerializer

    def get_queryset(self):
        filter = {}

        if "aoi_id" in self.kwargs:
            filter["aoi_id"] = self.kwargs["aoi_id"]

        return PrismDir.objects.filter(**filter)


class HRUZonesViewSet(UploadMixin, UpdateMixin, DownloadMixin,
                      BaseViewSet):
    serializer_class = HRUZonesSerializer

    def get_queryset(self):
        filter = {}

        if "aoi_id" in self.kwargs:
            filter["aoi_id"] = self.kwargs["aoi_id"]

        return HRUZones.objects.filter(**filter)


class HRUZonesDataViewSet(BaseViewSet):
    serializer_class = HRUZonesDataSerializer
    queryset = HRUZonesData.objects.all()
