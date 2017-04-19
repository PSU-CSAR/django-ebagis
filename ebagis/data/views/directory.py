from __future__ import absolute_import

from ...views.filters import make_model_filter

from ..models.zones import HRUZones, HRUZonesData
from ..models.directory import PrismDir, Maps

from ..serializers.data import (
    HRUZonesSerializer, HRUZonesDataSerializer, PrismDirSerializer,
    MapsSerializer
)

from .base import BaseViewSet
from .mixins import UploadMixin, UpdateMixin, DownloadMixin


class PrismViewSet(UploadMixin, UpdateMixin, DownloadMixin,
                   BaseViewSet):
    serializer_class = PrismDirSerializer
    _query_class = PrismDir
    search_fields = ("name",)
    filter_class = make_model_filter(PrismDir)

    @property
    def _filter_args(self):
        filter = {}

        if "aoi_id" in self.kwargs:
            filter["aoi_id"] = self.kwargs["aoi_id"]

        return filter


class MapsViewSet(UploadMixin, UpdateMixin, DownloadMixin,
                  BaseViewSet):
    serializer_class = MapsSerializer
    _query_class = Maps

    @property
    def _filter_args(self):
        filter = {}

        if "aoi_id" in self.kwargs:
            filter["aoi_id"] = self.kwargs["aoi_id"]

        return filter


class HRUZonesViewSet(UploadMixin, UpdateMixin, DownloadMixin,
                      BaseViewSet):
    serializer_class = HRUZonesSerializer
    _query_class = HRUZones

    @property
    def _filter_args(self):
        filter = {}

        if "aoi_id" in self.kwargs:
            filter["aoi_id"] = self.kwargs["aoi_id"]

        return filter


class HRUZonesDataViewSet(BaseViewSet):
    serializer_class = HRUZonesDataSerializer
    queryset = HRUZonesData.objects.all()
    _query_class = HRUZonesData
