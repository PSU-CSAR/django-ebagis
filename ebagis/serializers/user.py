from __future__ import absolute_import

from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers
from rest_framework.reverse import reverse


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username')


class UserDetailSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    def get_roles(self, obj):
        user = obj
        roles = []

        if user and user.is_staff:
            roles.append["ROLE_STAFF"]
        if user and user.is_superuser:
            roles.append["ROLE_ADMIN"]

        return roles

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'roles')
        read_only_fields = ('email', 'roles')


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
