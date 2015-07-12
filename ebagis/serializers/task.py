from __future__ import absolute_import

from rest_framework import serializers
from rest_framework.reverse import reverse

from djcelery.models import TaskMeta


class AOITaskSerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField()

    def get_result(self, obj):
        if obj.status == 'SUCCESS':
            return reverse('aoi-detail',
                           kwargs={'pk': obj.result},
                           request=self.context['request'])
        else:
            return obj.result

    class Meta:
        model = TaskMeta
