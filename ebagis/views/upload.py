from __future__ import absolute_import

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
from ..tasks import process_upload


class UploadView(ChunkedUploadView):
    model = Upload
    serializer_class = UploadSerializer

    def on_completion(self, upload, request):
        result = process_upload.delay(upload.id)
        upload.task, created = \
            TaskMeta.objects.get_or_create(task_id=result.task_id)
        upload.save()

    @classmethod
    def new_upload(cls, upload_model_class, request,
                   object_id=None,
                   parent_object_instance=None):
        """
        """
        # once we have modified the upload request appropriately, we
        # can call this view again with the defaul method and it will
        # create the upload from our new request object
        upload_view = cls()

        print request
        print request.data

        # set the upload object content_type
        upload_model_class_name_lower = upload_model_class.__name__.lower()
        print upload_model_class_name_lower
        request.data["content_type"] = \
            ContentType.objects.get(model=upload_model_class_name_lower).pk

        # we will assume the upload is an update
        # until proven otherwise
        is_update = True

        # if no object_id is passed in then we know that the
        # upload is not an update, and we need to generate an
        # object id for it. The object id would be automatically
        # created, but we explicitly set it here to allow it
        # to be returned before the upload is processed
        if not object_id:
            object_id = cls.generate_upload_UUID(upload_model_class)
            is_update = False

        # set the id and update values
        request.data["object_id"] = object_id
        request.data["is_update"] = is_update

        # if a parent object is supplied, we need to
        # get its content_type and id, then add those
        # parameters to our request
        if parent_object_instance:
            request.data["parent_content_type"] = \
                ContentType.objects.get_for_model(parent_object_instance).pk
            request.data["parent_object_id"] = \
                parent_object_instance.id

        print request
        print request.data
        logging.info(request.data)

        if request.method == 'PUT':
            return upload_view.put(request)
        elif request.method == 'POST':
            return upload_view.post(request)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def generate_upload_UUID(model):
        """Generate a random UUID that is not already the
        id of an instance of model"""
        while True:
            # create a random 128-bit UUID
            id = uuid.uuid4()

            # if an object does not already have that UUID
            # then we can use it and break out of the loop
            try:
                model.objects.get(pk=id)
            except model.DoesNotExist:
                break

        return id
