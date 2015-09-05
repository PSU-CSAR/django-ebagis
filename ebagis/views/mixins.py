from rest_framework import viewsets


class MultiSerializerViewSet(viewsets.ModelViewSet):
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


class LoadableViewSet(viewsets.ModelViewSet):
    """Provides generic create, update, and download
    views for a model object that supports such "load"
    operations."""

    @property
    def _model(self):
        return self.queryset.model

    def create(self, request, *args, **kwargs):
        return UploadView.new_upload(self._model, request)

    @detail_route
    def update(self, request, *args, **kwargs):
        object = self.get_object()
        return UploadView.new_upload(self._model, request, object_id=object.id)

    @detail_route()
    def download(self, request, *args, **kwargs):
        object = self.get_object()
        return DownloadViewSet.new_download(object, request)

