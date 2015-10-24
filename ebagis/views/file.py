from django.contrib.contenttypes.models import ContentType

from ..models import File

from ..serializers.data import FileSerializer

from .mixins import UploadMixin, UpdateMixin, DownloadMixin
from .base import BaseViewSet


class FileViewSet(UploadMixin, UpdateMixin, DownloadMixin,
                  BaseViewSet):
    serializer_class = FileSerializer

    def get_queryset(self):
        filter = {}

        # get file class to build queryset defaulting to
        # base File class if not set
        file_type = self.kwargs.get("file_type", None)
        if not file_type:
            file_type = File

        if "geodatabase_id" in self.kwargs:
            filter["object_id"] = self.kwargs["geodatabase_id"]
        elif (file_type.__class__.__name__ == "XML" and "zones" in self.kwargs) or "prism" in self.kwargs:
            filter["object_id"] = self.kwargs["version_id"]
        elif "zones" in self.kwargs and "geodatabase_type" in self.kwargs:
            filter["object_id"] = self.kwargs["geodatabase_type"].objects.get(
                hruzonesdata=self.kwargs["version_id"]
            )
        elif "geodatabase_type" in self.kwargs and "aoi_id" in self.kwargs:
            filter["content_type"] = ContentType.objects.get_for_model(
                self.kwargs["geodatabase_type"],
                for_concrete_model=False,
            )
            filter["aoi_id"] = self.kwargs["aoi_id"]

        return file_type.objects.filter(**filter)
