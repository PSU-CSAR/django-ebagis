from __future__ import absolute_import

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers

from djcelery.models import TaskMeta


class TaskSerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField()

    def get_result(self, obj):
        if obj.status == 'SUCCESS':
            try:
                pk, content_type = obj.result.split(",")
            except (AttributeError, ValueError):
                pass
            else:
                upload_class = ContentType.model_class(
                    ContentType.objects.get(model=content_type)
                )
                try:
                    return upload_class.objects.get(pk=pk).get_url(
                        self.context['request']
                    )
                except ObjectDoesNotExist:
                    return "object has been deleted"

        return obj.result

    class Meta:
        fields = '__all__'
        model = TaskMeta
