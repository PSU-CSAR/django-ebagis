from drf_chunked_upload.views import ChunkedUploadView

from djcelery.models import TaskMeta

# model objects
from ..models.upload import AOIUpload, UpdateUpload

# serializers
from ..serializers.upload import AOIUploadSerializer, UpdateUploadSerializer

# other
from ..tasks import add_aoi


class AOIUploadView(ChunkedUploadView):
    model = AOIUpload
    serializer_class = AOIUploadSerializer

    def on_completion(self, upload, request):
        result = add_aoi.delay(upload.id)
        upload.task, created = \
            TaskMeta.objects.get_or_create(task_id=result.task_id)
        upload.save()


class UpdateUploadView(ChunkedUploadView):
    model = UpdateUpload
    serializer_class = UpdateUploadSerializer

