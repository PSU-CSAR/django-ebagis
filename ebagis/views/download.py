from __future__ import absolute_import

from django.contrib.contenttypes.models import ContentType

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from djcelery.models import TaskMeta

# model objects
from ..models.download import Download

# serializers
from ..serializers.download import DownloadSerializer

# other
from ..tasks import export_data

# utils
from ..utils.http import stream_file
from .filters import make_model_filter


class DownloadViewSet(viewsets.ModelViewSet):
    model = Download
    serializer_class = DownloadSerializer
    search_fields = ("name",)
    filter_class = make_model_filter(model)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.file:
            return stream_file(instance.file.file.name, request)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def download(self, request, content_type, object_id):
        download = Download(user=request.user,
                            content_type=content_type,
                            object_id=object_id)
        download.save()
        result = export_data.delay(str(download.pk))
        download.task, created = \
            TaskMeta.objects.get_or_create(task_id=result.task_id)
        download.save()
        serializer = self.serializer_class(download,
                                           context={'request': request})
        return Response(serializer.data)

    @classmethod
    def new_download(cls, object, request):
        download_view = cls()
        if request.method == 'GET':
            return download_view.download(
                request,
                ContentType.objects.get_for_model(object),
                object.pk
            )
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
