from __future__ import absolute_import

from rest_framework import serializers

from .base import BaseSerializer
from .mixins import URLMixin


class FileDataSerializer(BaseSerializer):
    encoding = serializers.CharField(max_length=20)


class FileSerializer(URLMixin, BaseSerializer):
    versions = FileDataSerializer(read_only=True, many=True)


class GeodatabaseSerializer(URLMixin, BaseSerializer):
    rasters = FileSerializer(read_only=True, many=True)
    vectors = FileSerializer(read_only=True, many=True)
    tables = FileSerializer(read_only=True, many=True)


class PrismDirSerializer(URLMixin, BaseSerializer):
    versions = GeodatabaseSerializer(read_only=True, many=True)


class HRUZonesDataSerializer(URLMixin, BaseSerializer):
    hruzonesgdb = GeodatabaseSerializer(read_only=True)
    paramgdb = GeodatabaseSerializer(read_only=True)
    xml = FileSerializer(read_only=True)


class HRUZonesSerializer(URLMixin, BaseSerializer):
    versions = HRUZonesDataSerializer(read_only=True, many=True)
