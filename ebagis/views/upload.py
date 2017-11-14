from __future__ import absolute_import

from django.contrib.contenttypes.models import ContentType

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

from drf_chunked_upload.views import ChunkedUploadView

from djcelery.models import TaskMeta

# model objects
from ..models.upload import Upload

# serializers
from ..serializers.upload import UploadSerializer, UploadCreateSerializer

# other
from ..tasks import process_upload
from ..permissions import IsNwccWrite, IsOwnerOrAdmin
from ..utils.validation import generate_uuid
from ..utils.queries import owner_or_admin, get_object_owner_or_admin

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


# TODO: make into detail_route on UploadView
# but have to rework drf-chunked-upload to make
# ChunkedUploadView a viewset, not a class-based view
@api_view(['POST'])
@permission_classes((IsOwnerOrAdmin,))
def cancel_upload(request, pk):
    query = {'pk': pk}
    if not (request.user.groups.filter(name='NWCC_ADMIN').exists() or
            request.user.is_superuser):
        # non-admin users can only get their own uploads
        query['user'] = request.user

    try:
        upload = Upload.objects.get(**query)
    except Upload.DoesNotExist:
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
    serializer_class = UploadCreateSerializer
    search_fields = ("filename",)
    filter_class = make_model_filter(model,
                                     base=UploadFilterSet,
                                     exclude_fields=['file'])
    permission_classes = (IsNwccWrite,)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request is None or self.request.method not in ['PUT', 'POST']:
            serializer_class = UploadCreateSerializer
        return serializer_class

    def get_object(self):
        return get_object_owner_or_admin(self)

    def get_queryset(self):
        """
        Get (and filter) Upload queryset.
        By default, user can only continue uploading his/her own uploads.
        """
        query = self.model.objects.all()
        return owner_or_admin(query, self.request)

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
