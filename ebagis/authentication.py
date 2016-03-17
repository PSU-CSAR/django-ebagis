from __future__ import absolute_import

from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

from .models import ExpiringToken


class ExpiringTokenAuthentication(TokenAuthentication):
    model = ExpiringToken

    def authenticate_credentials(self, key):
        user, token = super(
            ExpiringTokenAuthentication, self
        ).authenticate_credentials(key)

        if not token.is_valid:
            raise exceptions.AuthenticationFailed('Invalid token')

        return (token.user, token)
