from __future__ import absolute_import

from rest_framework import viewsets


# so the idea here for getting a detail view without a pk is to override the
# default detail method with one that will take an optional pk. Then, if no
# pk is provided, it will use the enclosing object (AOI) that is provided
# to find the pk to use, which it will pass to the default detail method
# via the super function.


class BaseViewSet(viewsets.ModelViewSet):
    _filter_args = None
    _prefetch_related_fields = None
    _related_fields = None

    def get_queryset(self):
        return self._query_class.objects.filter(**self._filter_args)

    def get_object(self):
        if "pk" not in self.kwargs:
            return self._query_class.objects.get(**self._filter_args)
        else:
            return super(BaseViewSet, self).get_object()
