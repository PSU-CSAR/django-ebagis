from rest_framework.decorators import detail_route

from .upload import UploadView
from .download import DownloadViewSet


class MultiSerializerMixin(object):
    """Allows multiple serializers to be defined for a ModelViewSet.

    Use like:

    class SomeViewSet(MultiSerializerViewSet):
        model = models.SomeModel

        serializers = {
            'default': serializers.SomeModelSerializer
            'list':    serializers.SomeModelListSerializer,
            'detail':  serializers.SomeModelDetailSerializer,
            # etc.
        }
    """
    serializers = {
        'default': None,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action,
                                    self.serializers['default'])


class UploadMixin(object):
    """Overrides the default viewset create method to
    use the UploadView's new_upload method to make a
    new Upload instance to accept and process files
    for whatever object was "created"
    """
    def create(self, request, *args, **kwargs):
        parent_object = kwargs.get('parent_object', None)
        return UploadView.new_upload(self.queryset.model,
                                     request,
                                     parent_object_instance=parent_object)


class UpdateMixin(object):
    """Adds a new viewset method to allow update
    uploads using the UploadView's new_upload method.
    This will make a new Upload instance to accept
    and process files for whatever object is to be
    updated, passing in that object's id so the
    upload knows that this is an update, not a create.
    """
    @detail_route
    def update(self, request, *args, **kwargs):
        object = self.get_object()
        return UploadView.new_upload(self.queryset.model,
                                     request,
                                     object_id=object.id)


class DownloadMixin(object):
    """Adds a new viewset method to allow downloads.
    This uses the DownloadViewSet's new_download
    method to make a new Download instance that will
    assemble the files into a .zip.
    """
    @detail_route()
    def download(self, request, *args, **kwargs):
        object = self.get_object()
        return DownloadViewSet.new_download(object, request)

