from __future__ import absolute_import

from rest_framework import serializers

from .download import DownloadSerializer
from .task import TaskSerializer
from .upload import UploadSerializer
from .user import UserSerializer, GroupSerializer, PermissionSerializer

