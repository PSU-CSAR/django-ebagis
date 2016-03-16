from __future__ import absolute_import
import logging
import mimetypes

from django.contrib.contenttypes.models import ContentType
from django.http import StreamingHttpResponse

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


logger = logging.getLogger(__name__)


class DownloadViewSet(viewsets.ModelViewSet):
    queryset = Download.objects.all()
    serializer_class = DownloadSerializer

    def retrieve(self, request, *args, **kwargs):
        import os
        import re
        from ..utils.filesystem import FileWrapper
        from ..constants import CHUNK_SIZE
        #import pdb; pdb.set_trace()

        instance = self.get_object()

        if instance.file:
            file_path = instance.file.file.name
            file_size = os.path.getsize(file_path)
            start = 0
            end = None

            if "HTTP_RANGE" in request.META:
                try:
                    start, end = re.findall(r"/d+", request.META["HTTP_RANGE"])
                except TypeError:
                    logger.exception(
                        "Malformed HTTP_RANGE in download request: {}"
                        .format(request.META["HTTP_RANGE"])
                    )
                    return Response(
                        status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
                    )

                if start > end or end > file_size:
                    return Response(
                        status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
                    )

            fwrapper = FileWrapper(
                open(file_path, 'rb'),
                blksize=CHUNK_SIZE,
                start=start,
                end=end
            )
            response = StreamingHttpResponse(
                fwrapper,
                content_type=mimetypes.guess_type(file_path)[0]
            )
            name = os.path.basename(file_path)
            response["Content-Disposition"] = \
                'attachment; filename="' + name + '"'
            response["Content-Length"] = file_size
            response["Accept-Ranges"] = 'bytes'

            if "HTTP_RANGE" in request.META:
                response["status"] = 206
                response["Content-Range"] = "bytes {}-{}/{}".format(start,
                                                                    end,
                                                                    file_size)

            return response

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
