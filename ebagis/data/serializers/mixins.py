from __future__ import absolute_import

from rest_framework import serializers


class URLMixin(serializers.Serializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return obj.get_url(self.context['request'])
