from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, ))
def validate_token(request):
    if request.method == 'GET':
        return Response({"message": "you're logged in", "user": request.user.username})

