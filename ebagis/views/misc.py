from __future__ import absolute_import
import logging
import yaml

from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status

from ..models import ExpiringToken
from ..authentication import ExpiringTokenAuthentication

from ..settings import DESKTOP_SETTINGS, LAYER_FILE

from ..utils.http import stream_file


logger = logging.getLogger(__name__)


@api_view(["GET"])
@authentication_classes((ExpiringTokenAuthentication, ))
@permission_classes((IsAuthenticated, ))
def validate_token(request):
    if request.method == "GET":
        return Response({
            "message": "you're logged in",
            "user": request.user.username,
            "warning":
                "this endpoint is deprecated -- use /api/rest/account/user/",
        })


class ObtainExpiringAuthToken(ObtainAuthToken):
    permission_classes = (AllowAny, )

    def post(self, request, token_field="token"):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = ExpiringToken.objects.get_or_create(user=user)
        if not created and not token.is_valid:
            token.update()
        return Response({token_field: str(token), "created": created})


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def delete_auth_token(request):
    request.user.token.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def get_settings(request, module='bagis'):
    # load the desktop settings yaml file;
    # to increase performance, the could be placed outside
    # the function, so the file would only be loaded once,
    # but then changes would require restarting the process
    # I think that would constitute premature optimization
    # with a rather significant drawback
    with open(DESKTOP_SETTINGS, 'r') as fstream:
        desktop_settings = yaml.safe_load(fstream)
    try:
        return Response(desktop_settings[module])
    except KeyError:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def get_lyr(request):
    return stream_file(LAYER_FILE, request)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def check_api_version(request):
    return Response(float(request.version))
