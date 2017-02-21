from __future__ import absolute_import

from django.contrib.contenttypes.models import ContentType

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from drf_chunked_upload.views import ChunkedUploadView

from djcelery.models import TaskMeta

# model objects
from ..models.upload import Upload

# serializers
from ..serializers.upload import UploadSerializer

# other
from ..tasks import process_upload
from ..utils.validation import generate_uuid
from ..utils.queries import admin_queryset_filter

from .filters import (
    CreatedAtMixin, FilterSet, make_model_filter, filters
)


class CreatedByMixin(FilterSet):
    user_field = "user"
    created_by = filters.CharFilter(
        name="{}__username".format(user_field),
        lookup_expr="icontains",
    )

    class Meta:
        abstract = True


class UploadFilterSet(CreatedAtMixin, CreatedByMixin, FilterSet):
    class Meta:
        abstract = True


@api_view(['POST'])
def cancel_upload(request, pk):

    try:
        if request.user.is_superuser:
            # allow admin users to get any user's upload
            upload = Upload.objects.get(pk=pk)
        else:
            # normal users can only get their own uploads
            upload = Upload.objects.get(pk=pk, user=request.user)
    except upload.DoesNotExist:
        # per queries above, this could be thrown even
        # if an upload exists such as when a user tries
        # to call this on an upload that is not theirs
        # and they are not admin
        return Response(status=status.HTTP_404_NOT_FOUND)

    cancelled = upload.cancel()

    if cancelled is True:
        return Response(status=status.HTTP_200_OK)
    elif cancelled is False:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


class UploadView(ChunkedUploadView):
    model = Upload
    serializer_class = UploadSerializer
    search_fields = ("filename",)
    filter_class = make_model_filter(model,
                                     base=UploadFilterSet,
                                     exclude_fields=['file'])

    def get_queryset(self):
        """
        Get (and filter) Upload queryset.
        By default, user can only continue uploading his/her own uploads.
        """
        query = self.model.objects.all()
        return admin_queryset_filter(query, self.request)

    def on_completion(self, upload, request):
        result = process_upload.delay(str(upload.id))
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

        # request.data is a QueryDict instance and may be immutable;
        # set the _mutable parameter to true so we can modify as needed
        request.data._mutable = True

        # set the upload object content_type
        upload_model_class_name_lower = upload_model_class.__name__.lower()
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
            object_id = generate_uuid(upload_model_class)
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

        if request.method == 'PUT':
            return upload_view.put(request)
        elif request.method == 'POST':
            return upload_view.post(request)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
