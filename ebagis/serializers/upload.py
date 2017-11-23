from __future__ import absolute_import

from django.core.exceptions import ValidationError

from rest_framework import serializers

from ..models.upload import Upload

from .task import TaskSerializer
from .fields import FriendlyChoiceField


class UploadSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="upload-detail")
    user = serializers.HyperlinkedRelatedField(view_name="user-detail",
                                               read_only=True)
    task = TaskSerializer(read_only=True)
    status = FriendlyChoiceField(choices=Upload.STATUS_CHOICES, required=False)

    def validate(self, data):
        model = data['content_type'].model_class()

        if hasattr(model, 'validate'):
            try:
                model.validate(data)
            except ValidationError as e:
                raise serializers.ValidationError(e[0])

        return data

    class Meta:
        model = Upload
        exclude = ('file', )
        read_only_fields = (
            'id', 'status', 'completed_at', 'task', 'offset', 'md5'
        )


class UploadCreateSerializer(UploadSerializer):
    class Meta:
        model = Upload
        fields = '__all__'
        read_only_fields = (
            'id', 'status', 'completed_at', 'task', 'offset', 'md5'
        )
