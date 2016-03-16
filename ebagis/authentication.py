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

#        model = self.get_model()
#        try:
#            token = model.objects.get(key=key)
#        except model.DoesNotExist:
#            raise exceptions.AuthenticationFailed('Invalid token')
#
#        if not token.user.is_active:
#            raise exceptions.AuthenticationFailed('User inactive or deleted')

        if not token.is_valid:
            raise exceptions.AuthenticationFailed('Invalid token')

        return (token.user, token)
