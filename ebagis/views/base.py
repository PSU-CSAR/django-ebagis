from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

# so the idea here for getting a detail view without a pk is to override the
# default detail method with one that will take an optional pk. Then, if no
# pk is provided, it will use the enclosing object (AOI) that is provided
# to find the pk to use, which it will pass to the default detail method
# via the super function.

class BaseViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        raise NotImplementedError

    def retrieve(self, request, pk=None, *args, **kwargs):
        if not pk:
            queryset = self.filter_queryset(self.get_queryset())

            if not queryset.count() == 1:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            pk = queryset[0].pk

        return super(BaseViewSet, self).retrieve(request, pk, *args, **kwargs)

