import logging
logger = logging.getLogger(__name__)

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

# so the idea here for getting a detail view without a pk is to override the
# default detail method with one that will take an optional pk. Then, if no
# pk is provided, it will use the enclosing object (AOI) that is provided
# to find the pk to use, which it will pass to the default detail method
# via the super function.


class BaseViewSet(viewsets.ModelViewSet):

    #def get_queryset(self):
    #    raise NotImplementedError

    def get_object(self):
        logger.debug(self.kwargs)
        if "pk" not in self.kwargs:
            queryset = self.filter_queryset(self.get_queryset())
            logger.debug("\ntt\n")
            try:
                if not len(queryset) == 1:
                    return None
            except TypeError:
                return queryset
            else:
                return queryset[0]
        else:
            logger.debug("\nff\n")
            return super(BaseViewSet, self).get_object()
