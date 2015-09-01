import logging
import uuid

from django.contrib.contenttypes.models import ContentType

from rest_framework.response import Response
from rest_framework import status

from drf_chunked_upload.views import ChunkedUploadView

from djcelery.models import TaskMeta

# model objects
from ..models.upload import Upload

# serializers
from ..serializers.upload import UploadSerializer

# other
from ..tasks.upload import process_upload


class UploadView(ChunkedUploadView):
    model = Upload
    serializer_class = UploadSerializer

    def on_completion(self, upload, request):
        result = process_upload.delay(upload.id)
        upload.task, created = \
            TaskMeta.objects.get_or_create(task_id=result.task_id)
        upload.save()

    @classmethod
    def new_upload(cls, upload_model, request, update=False):
        """
        """
        upload_view = cls()

        # set the content_type and generate an object_id
        # the object id would be automatically created,
        # but we explicitly set it here to allow it
        # to be returned before the upload is processed
        request.data["content_type"] = ContentType.objects.get_for_model(upload_model)
        request.data["object_id"] = cls.generate_upload_UUID(upload_model)
        request.data["update"] = update

        logging.info(request.data)

        if request.method == 'PUT':
            return upload_view.put(request)
        elif request.method == 'POST':
            return upload_view.post(request)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def generate_upload_UUID(model):
        """Generate a random UUID that is not already the
        id of an instance of model"""
        while True:
            # create a random 128-bit UUID
            id = uuid.uuid4()

            # if an object does not already have that UUID
            # then we can use it and break out of the loop
            if not model.objects.get(pk=id):
                break

        return id
