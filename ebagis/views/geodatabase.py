from rest_framework import viewsets

from ..models.aoi import Geodatabase

from ..serializers.geodatabase import GeodatabaseSerializer

from .mixins import UpdateMixin, DownloadMixin


class GeodatabaseViewSet(UpdateMixin, DownloadMixin,
                         viewsets.ModelViewSet):
    serializers = GeodatabaseSerializer

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
        else:
            return None

        return geodatabase_type.objects.get(**filter)

