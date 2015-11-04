from __future__ import absolute_import

from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from ..models.upload import Upload
from ..utils.validation import validate_path

from .task import TaskSerializer


class UploadSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="upload-detail")
    user = serializers.HyperlinkedRelatedField(view_name="user-detail",
                                               read_only=True)
    task = TaskSerializer(read_only=True)
    md5 = serializers.CharField(required=False)

# TODO: move the validation to the model classes, and call the necessary methods here
#    def validate(self, data):
#        if not data.is_update:
#            if data.parent_object_id:
#                parent_class = ContentType.model_class(data.parent_content_type)
#                parent_object = parent_class.objects.get(pk=data.parent_object_id)
#
#            name = os.path.splitext(value)[0]
#            validate_path(name, allow_whitespace=True)
#            upload_class = ContentType.model_class(data.content_type)
#
#            try:
#                upload_class.objects.get(name)
#            except upload_class.DoesNotExist:
#                pass
#            else:
#                raise serializers.ValidationError("An object of the same name and type already exists.")
#
#        return data

    class Meta:
        model = Upload
        read_only_fields = (
            'id', 'status', 'completed_at', 'task', 'offset',
        )
