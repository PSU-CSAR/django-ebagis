from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse


class APIRoot(APIView):
    def get(self, request):
        return Response({
            'AOIs': reverse('aoi-base:list', request=request),
            'Uploads': reverse('upload-list', request=request),
            'Downloads': reverse('download-list', request=request),
            'Users': reverse('user-list', request=request),
            'Groups': reverse('group-list', request=request),
        })

