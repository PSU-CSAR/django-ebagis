from __future__ import absolute_import

from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken

from ..models import ExpiringToken


@api_view(["GET"])
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, ))
def validate_token(request):
    if request.method == "GET":
        return Response({"message": "you're logged in",
                         "user": request.user.username})


class ObtainExpiringAuthToken(ObtainAuthToken):
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = ExpiringToken.objects.get_or_create(user=user)
        if not created and not token.is_valid:
            token.update()
        return Response({'token': str(token), 'created': created})
