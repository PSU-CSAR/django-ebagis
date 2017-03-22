from __future__ import absolute_import

from six import iteritems

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
        file_class = self.kwargs.get("file_class", None)
        if not file_class:
            file_class = File
        return file_class

    @property
    def _filter_args(self):
        _set_parent = True
        _set_directory = False
        filter = {}

        if self.kwargs.get("generation_skip", False) and \
                "directory_type" in self.kwargs and \
                "parent_id" in self.kwargs:
            # If the generation_skip is set, we also need the
            # directory_type and parent_id to be set for it to
            # be useful. With all three, we know that the parent_id
            # actually is the parent's parent, and that the directory
            # type is the current object's parent--hence, the parent
            # id "skips a generation".
            filter["_parent_object___parent_object"] = self.kwargs["parent_id"]
            # we use the following as "short cuts" so we know
            # if we need to use certain kwargs args again
            _set_parent = False
            _set_directory = True

        # if we found the parent id before, then we
        # used it above and don't want to use it here
        if _set_parent and "parent_id" in self.kwargs:
            filter["_parent_object"] = self.kwargs["parent_id"]

        # if we found the directory type before, then we
        # know we can set it here and don't need to check
        if _set_directory or "directory_type" in self.kwargs:
            filter["_parent_object__classname"] = \
                self.kwargs["directory_type"].__name__

        if "aoi_id" in self.kwargs:
            filter["aoi_id"] = self.kwargs["aoi_id"]

        if "literal_filters" in self.kwargs:
            for key, val in iteritems(self.kwargs["literal_filters"]):
                filter[key] = val

        return filter
