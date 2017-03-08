from __future__ import absolute_import

from rest_framework import serializers
from ..models.download import Download
from .task import TaskSerializer


class DownloadSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="download-detail")
    user = serializers.HyperlinkedRelatedField(view_name="user-detail",
                                               read_only=True)
    task = TaskSerializer(read_only=True)

    class Meta:
        model = Download
        fields = '__all__'
        read_only_fields = ('status', 'completed_at', 'task', 'name')
