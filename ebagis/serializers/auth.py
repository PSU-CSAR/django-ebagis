from urlparse import urlparse
from rest_framework import serializers
from rest_auth.serializers import PasswordResetSerializer as PRS
from rest_auth.registration.serializers import RegisterSerializer as RS


def get_user_field_max_length(field_name):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User._meta.get_field(field_name).max_length


class RegisterSerializer(RS):
    first_name = serializers.CharField(
        max_length=get_user_field_max_length('first_name')
    )
    last_name = serializers.CharField(
        max_length=get_user_field_max_length('last_name')
    )

    def get_cleaned_data(self):
        data = super(RegisterSerializer, self).get_cleaned_data()
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        return data


class PasswordResetSerializer(PRS):
    def get_email_options(self):
        """Overriding default method to provide custom arguements"""
        request = self.context.get('request')
        origin = urlparse(request.META['HTTP_ORIGIN'])
        opts = {
            'extra_email_context': {
                'reset_url': request.data.get('reset_url', None),
                'site_name': request.data.get('site_name', 'ebagis'),
            },
            'domain_override': origin.netloc,
            'use_https': origin.scheme == 'https',
        }
        return opts
