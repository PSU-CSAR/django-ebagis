from __future__ import absolute_import
from django.contrib.contenttypes.models import ContentType

from ..models import File

from ..serializers.data import FileSerializer

from .mixins import UploadMixin, UpdateMixin, DownloadMixin
from .base import BaseViewSet


class FileViewSet(UploadMixin, UpdateMixin, DownloadMixin,
                  BaseViewSet):
    serializer_class = FileSerializer

    @property
    def _query_class(self):
        # get file class to build queryset defaulting to
        # base File class if not set
        file_type = self.kwargs.get("file_type", None)
        if not file_type:
            file_type = File
        return file_type

    @property
    def _filter_args(self):
        filter = {}

        if "geodatabase_id" in self.kwargs:
            filter["object_id"] = self.kwargs["geodatabase_id"]
        elif (self._query_class.__class__.__name__ == "XML" and
              "zones" in self.kwargs) or "prism" in self.kwargs:
            filter["object_id"] = self.kwargs["version_id"]
        elif "zones" in self.kwargs and "geodatabase_type" in self.kwargs:
            filter["object_id"] = self.kwargs["geodatabase_type"].objects.get(
                hru_zones_data=self.kwargs["version_id"]
            ).id
        elif "geodatabase_type" in self.kwargs and "aoi_id" in self.kwargs:
            filter["content_type"] = ContentType.objects.get_for_model(
                self.kwargs["geodatabase_type"],
                for_concrete_model=False,
            )
            filter["aoi_id"] = self.kwargs["aoi_id"]

        return filter
