from __future__ import absolute_import

from rest_framework import serializers

from ..models.file_data import (
    FileData, XMLData, RasterData, VectorData, TableData, MapDocumentData,
)

from .user import UserSerializer


class FileDataSerializer(serializers.ModelSerializer):
#    url = serializers.SerializerMethodField()
#
#    def get_url(self, obj):
#        name_key = URL_FILTER_QUERY_ARG_PREFIX + "name__iexact"
#
#        kwargs = {
#            URL_FILTER_QUERY_ARG_PREFIX + "aoi_id": obj.content_object.aoi_id,
#            "pk": obj.id,
#            name_key: obj.content_object.name.lower(),
#        }
#
#        if kwargs[name_key] in MULTIPLE_GDBS:
#            kwargs[URL_FILTER_QUERY_ARG_PREFIX + "__object_id"] = obj.object_id
#
#        return reverse('geodatabase-' + type(obj).__name__.lower() + '-detail',
#                       kwargs=kwargs,
#                       request=self.context['request'])

    created_by = UserSerializer(read_only=True)

    class Meta:
        model = FileData


class XMLDataSerializer(FileDataSerializer):
    class Meta:
        model = XMLData


class VectorDataSerializer(FileDataSerializer):
    class Meta:
        model = VectorData


class RasterDataSerializer(FileDataSerializer):
    class Meta:
        model = RasterData


class TableDataSerializer(FileDataSerializer):
    class Meta:
        model = TableData
