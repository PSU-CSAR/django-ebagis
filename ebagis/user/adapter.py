'''override of django-allauth account adapter class; for an example of why see
http://django-allauth.readthedocs.io/en/latest/advanced.html#custom-redirects
'''
from __future__ import absolute_import
from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    def add_message(self, request, level, message_template,
                    message_context=None, extra_tags=''):
        '''modified rest_auth RegisterView.perform_create so it passes in
        a drf request object. However, django has a problem with a
        non-HttpRequest object, so we have to override this method to pull
        the HttpRequest object out of the Request object and pass that in
        to the original add_message adapter method.
        '''
        try:
            request = request._request
        except AttributeError:
            pass

        super(AccountAdapter, self).add_message(
            request,
            level,
            message_template,
            message_context=message_context,
            extra_tags=extra_tags
        )

    def get_email_confirmation_url(self, request, emailconfirmation):
        '''allow passing in a url with the request'''
        try:
            activation_url = request.data['activation_url']
        except (AttributeError, KeyError):
            # if the reqest did not have data, or the url was
            # unspecificed, then we'll do things the old way
            activation_url = super(AccountAdapter, self)\
                .get_email_confirmation_url(request, emailconfirmation)
        else:
            # else we have what we need minus the domain name and key
            activation_url = request.META['HTTP_ORIGIN'] \
                + activation_url + emailconfirmation.key

        return activation_url
