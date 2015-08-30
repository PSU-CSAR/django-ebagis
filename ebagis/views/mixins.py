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

