from __future__ import absolute_import

from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

# model objects
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

# serializers
from ..serializers.user import (
    UserSerializer, GroupSerializer, PermissionSerializer,
    UserDetailSerializer,
)

from ..utils import user


class UserDetailsView(RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = get_user_model().objects.filter(is_active=True)
    serializer_class = UserSerializer
    search_fields = ("username", "email")

    def perform_destroy(self, instance):
        user.deactivate(instance)


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
