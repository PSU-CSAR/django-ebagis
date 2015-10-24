from __future__ import absolute_import

from ..models.geodatabase import Geodatabase

from ..serializers.data import GeodatabaseSerializer

from .base import BaseViewSet
from .mixins import UpdateMixin, DownloadMixin


class GeodatabaseViewSet(UpdateMixin, DownloadMixin,
                         BaseViewSet):
    serializer_class = GeodatabaseSerializer

    def get_queryset(self):
        filter = {}

        # get geodatabase class to build queryset defaulting to
        # base geodabase class if not set
        geodatabase_type = self.kwargs.get("geodatabase_type", None)
        if not geodatabase_type:
            geodatabase_type = Geodatabase

        if "zones" in self.kwargs:
            filter["hruzonesdata"] = self.kwargs["version_id"]
        elif "aoi_id" in self.kwargs:
            filter["aoi_id"] = self.kwargs["aoi_id"]

        return geodatabase_type.objects.filter(**filter)
