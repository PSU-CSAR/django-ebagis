from __future__ import absolute_import

import os

from rest_framework import serializers

from ..models.aoi import AOI
from ..models.upload import AOIUpload, UpdateUpload

from ..utilities import validate_path

from .task import AOITaskSerializer


class AOIUploadSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="aoiupload-detail")
    user = serializers.HyperlinkedRelatedField(view_name="user-detail",
                                               read_only=True)
    task = AOITaskSerializer(read_only=True)
    md5 = serializers.CharField(required=False)

    def validate_filename(self, value):
        aoi_name = os.path.splitext(value)[0]
        validate_path(aoi_name, allow_whitespace=True)

        try:
            AOI.objects.get(name=aoi_name)
        except AOI.DoesNotExist:
            pass
        else:
            raise Exception("An AOI of the same name already exists.")

        return value

    class Meta:
        model = AOIUpload
        read_only_fields = ('status', 'completed_at', 'task', 'offset')


class UpdateUploadSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="updateupload-detail")
    user = serializers.HyperlinkedRelatedField(view_name="user-detail",
                                               read_only=True)

    def validate_filename(self, value):
        file_name = os.path.splitext(value)
        validate_path(file_name)
        return value

    class Meta:
        model = UpdateUpload
        read_only_fields = ('status', 'completed_at', 'processed')
