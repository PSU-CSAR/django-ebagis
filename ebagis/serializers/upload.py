from __future__ import absolute_import
import os

from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from ..models.aoi import AOI
from ..models.upload import Upload

from ..utils.validation import validate_path

from .task import TaskSerializer


class UploadSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="aoiupload-detail")
    user = serializers.HyperlinkedRelatedField(view_name="user-detail",
                                               read_only=True)
    task = AOITaskSerializer(read_only=True)
    md5 = serializers.CharField(required=False)

    #def validate_filename(self, value):
    #    name = os.path.splitext(value)[0]
    #    validate_path(name, allow_whitespace=True)
    #    upload_class = ContentType.model_class(upload.content_type)
    #
    #    try:
    #        upload_class.objects.get(name)
    #    except upload_class.DoesNotExist:
    #        pass
    #    else:
    #        raise Exception("An object of the same name and type already exists.")
    #
    #    return value

    class Meta:
        model = Upload
        read_only_fields = (
            'status', 'completed_at', 'task', 'offset', 'content_type',
            'object_id', 'update',
        )

