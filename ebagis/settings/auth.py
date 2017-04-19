## callable to generate a token for rest auth login
#def get_expiring_token(token_class, user, serializer):
#    token, created = token_class.objects.get_or_create(user=user)
#    if not created and not token.is_valid:
#        token.update()
#    return token

INSTALLED_APPS += (
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    #'rest_auth.registration',
)

ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_ADAPTER = "ebagis.user.adapter.AccountAdapter"

#REST_SESSION_LOGIN = False,
#REST_AUTH_TOKEN_MODEL = 'ebagis.models.ExpiringToken'
#REST_AUTH_TOKEN_CREATOR = get_expiring_token
#REST_AUTH_REGISTER_SERIALIZERS = {
#    'REGISTER_SERIALIZER':
#        'ebagis.serializers.auth.RegisterSerializer',
#}

#REST_AUTH_SERIALIZERS = {
#    'USER_DETAILS_SERIALIZER':
#        'ebagis.serializers.user.UserDetailSerializer',
#    'PASSWORD_RESET_SERIALIZER':
#        'ebagis.serializers.auth.PasswordResetSerializer',
#}

# authentication settings
AUTHENTICATION_BACKENDS = (
    # basic django auth backend
    'django.contrib.auth.backends.ModelBackend',
)
