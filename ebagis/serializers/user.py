from __future__ import absolute_import

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from rest_framework.reverse import reverse


class PermissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    #url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse('user-detail',
                       args=[obj.user_id],
                       request=self.context['request'])

    class Meta:
        model = Group
        fields = 'name'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('url', 'username')


class UserDetailSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    def get_roles(self, obj):
        user = obj
        roles = []

        if user and user.is_staff:
            roles.append("ROLE_STAFF")
        if user and user.is_superuser:
            roles.append("ROLE_ADMIN")

        return roles

    def get_groups(self, obj):
        return [grp.name for grp in obj.groups.all()]

    class Meta:
        model = get_user_model()
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'roles',
            #'user_permissions',
            'groups',
        )
        read_only_fields = (
            'email',
            'roles',
            #'user_permissions',
            'groups',
        )
