from __future__ import absolute_import

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes


@permission_classes((AllowAny,))
class APIRoot(APIView):
    def get(self, request):
        return Response({
            'AOIs': reverse('aoi-base:list', request=request),
            'Uploads': reverse('upload-list', request=request),
            'Downloads': reverse('download-list', request=request),
            'Users': reverse('user-list', request=request),
            'Groups': reverse('group-list', request=request),
        })
