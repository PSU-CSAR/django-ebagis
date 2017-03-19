from __future__ import absolute_import

from rest_framework import serializers

from .user import UserSerializer


class BaseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    created_at = serializers.DateTimeField()
    removed_at = serializers.DateTimeField()
    name = serializers.CharField(max_length=100)
    parent_object = serializers.SerializerMethodField()
    comment = serializers.CharField(allow_blank=True)
    created_by = UserSerializer(read_only=True)

    def __init__(self, *args, **kwargs):
        """Custom init used to allow optional serializer fields
        that will be dropped if they do not contain data.

        Note that this is not currently used and can be removed
        without consequence if it causes problems."""
        # Don't pass the 'fields' arg up to the superclass
        optional_fields = kwargs.pop('optional_fields', [])

        # Instantiate the superclass normally
        super(BaseSerializer, self).__init__(*args, **kwargs)

        # Drop any null fields that are specified
        # in the `optional_fields` argument.
        for field_name in optional_fields:
            if not self.fields[optional_fields]:
                self.fields.pop(field_name)

    def get_parent_object(self, obj):
        parent = obj._parent_object
        url = None

        if parent:
            url = parent.get_url(self.context['request'])

        return url
