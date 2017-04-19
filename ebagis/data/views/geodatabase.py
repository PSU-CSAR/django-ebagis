from __future__ import absolute_import

from six import iteritems

from ..models.directory import Directory

from ..serializers.data import GeodatabaseSerializer

from .base import BaseViewSet
from .mixins import UpdateMixin, DownloadMixin


class GeodatabaseViewSet(UpdateMixin, DownloadMixin,
                         BaseViewSet):
    serializer_class = GeodatabaseSerializer

    @property
    def _query_class(self):
        # get geodatabase class to build queryset defaulting to
        # base geodabase class if not set
        directory_type = self.kwargs.get("directory_type", None)
        if not directory_type:
            directory_type = Directory
        return directory_type

    @property
    def _filter_args(self):
        filter = {}

        if "parent_id" in self.kwargs:
            filter["_parent_object"] = self.kwargs["parent_id"]

        if "aoi_id" in self.kwargs:
            filter["aoi_id"] = self.kwargs["aoi_id"]

        if "literal_filters" in self.kwargs:
            for key, val in iteritems(self.kwargs["literal_filters"]):
                filter[key] = val

        return filter
