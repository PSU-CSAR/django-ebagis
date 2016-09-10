from urlparse import urlparse
from rest_auth.serializers import PasswordResetSerializer as PRS


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
