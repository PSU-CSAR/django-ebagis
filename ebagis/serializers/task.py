from __future__ import absolute_import

from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers
from rest_framework.reverse import reverse

from djcelery.models import TaskMeta


class TaskSerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField()

    def get_result(self, obj):
        if obj.status == 'SUCCESS':
            pk, content_type = obj.result.split(",")

            # TODO: the reverse won't work, need to use id and content type
            # to find exact object instance and build URL from it

            upload_class = ContentType.model_class(
                ContentType.objects.get(model=content_type)
            )

            return upload_class.objects.get(pk=pk).get_url(
                self.context['request']
            )
        else:
            return obj.result

    class Meta:
        model = TaskMeta
