from __future__ import absolute_import

from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from djcelery.models import TaskMeta


class TaskSerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField()

    def get_result(self, obj):
        if obj.status == 'SUCCESS':
            try:
                pk, content_type = obj.result.split(",")
            except AttributeError:
                pass
            except ValueError:
                pass
            else:
                upload_class = ContentType.model_class(
                    ContentType.objects.get(model=content_type)
                )
                return upload_class.objects.get(pk=pk).get_url(
                    self.context['request']
                )

        return obj.result

    class Meta:
        fields = '__all__'
        model = TaskMeta
