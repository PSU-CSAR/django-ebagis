from __future__ import absolute_import

from rest_framework import viewsets


# so the idea here for getting a detail view without a pk is to override the
# default detail method with one that will take an optional pk. Then, if no
# pk is provided, it will use the enclosing object (AOI) that is provided
# to find the pk to use, which it will pass to the default detail method
# via the super function.


class BaseViewSet(viewsets.ModelViewSet):
    def get_object(self):
        if "pk" not in self.kwargs:
            queryset = self.filter_queryset(self.get_queryset())
            try:
                if not len(queryset) == 1:
                    return None
            except TypeError:
                return queryset
            else:
                return queryset[0]
        else:
            return super(BaseViewSet, self).get_object()
