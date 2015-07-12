from __future__ import absolute_import

from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers
from rest_framework.reverse import reverse


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username')


class PermissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Permission


class GroupSerializer(serializers.ModelSerializer):
    #url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse('user-detail',
                       args=[obj.user_id],
                       request=self.context['request'])

    class Meta:
        model = Group
