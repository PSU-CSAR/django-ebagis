from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.response import Response

from djcelery.models import TaskMeta

# model objects
from ..models.download import Download

# serializers
from ..serializers.download import DownloadSerializer

# other
from ..tasks import export_data


class DownloadViewSet(viewsets.ModelViewSet):
    queryset = Download.objects.all()
    serializer_class = DownloadSerializer

    def retrieve(self, request, *args, **kwargs):
        import os

        instance = self.get_object()

        if instance.file:
            response = HttpResponse(instance.file,
                                    content_type='application/zip')
            name = os.path.basename(instance.file.file.name)
            response['Content-Disposition'] = \
                'attachment; filename="' + name + '"'
            return response

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def download(self, request, content_type, object_id):
        download = Download(user=request.user,
                            content_type=content_type,
                            object_id=object_id)
        download.save()
        result = export_data.delay(download.id)
        download.task, created = \
            TaskMeta.objects.get_or_create(task_id=result.task_id)
        download.save()
        serializer = self.serializer_class(download,
                                           context={'request': request})
        return Response(serializer.data)

