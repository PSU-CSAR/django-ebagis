def get_expiring_token(token_class, user, serializer):
    token, created = token_class.objects.get_or_create(user=user)
    if not created and not token.is_valid:
        token.update()
    return token

SETUP_STR = "EBAGIS_IS_SETUP"


# apps to be appended to installed apps list in main settings
# these will be added via the setup function
EBAGIS_INSTALLED_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'drf_chunked_upload',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
]


# settings for the above apps
# these apply to django_ebagis only, not the whole site
# these will be set via the setup function
EBAGIS_APP_SETTINGS = {

    "ACCOUNT_AUTHENTICATION_METHOD": "username",
    "ACCOUNT_EMAIL_REQUIRED": True,
    "ACCOUNT_EMAIL_VERIFICATION": "mandatory",
    "ACCOUNT_DEFAULT_HTTP_PROTOCOL": "https",
    "ACCOUNT_ADAPTER": "ebagis.user.adapter.AccountAdapter",

    "REST_AUTH_TOKEN_MODEL":
        'ebagis.models.ExpiringToken',
    "REST_AUTH_TOKEN_CREATOR": get_expiring_token,
    "REST_AUTH_SERIALIZERS": {
        'USER_DETAILS_SERIALIZER':
            'ebagis.serializers.user.UserDetailSerializer',
        'PASSWORD_RESET_SERIALIZER':
            'ebagis.serializers.auth.PasswordResetSerializer',
    },

    "REST_FRAMEWORK": {
        # user authentication
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'ebagis.authentication.ExpiringTokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
            ),
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAdminUser',
            ),
        'PAGINATE_BY': 100,
        'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
        'DEFAULT_FILTER_BACKENDS': (
            'rest_framework.filters.DjangoFilterBackend',
            'rest_framework.filters.SearchFilter'
        ),
    },

    "SWAGGER_SETTINGS": {
        'exclude_namespaces': [],
        'api_version': '0.1',
        'enabled_methods': [
            'get',
            'post',
            'put',
            'patch',
            'delete'
        ],
        'api_key': 'special-key',
        'is_authenticated': False,
        'is_superuser': True,
        'permission_denied_handler': None,
        'info': {
            'contact': 'apiteam@wordnik.com',
            'description': 'This is a sample server Petstore server. '
                           'You can find out more about Swagger at '
                           '<a href="http://swagger.wordnik.com">'
                           'http://swagger.wordnik.com</a> '
                           'or on irc.freenode.net, #swagger. '
                           'For this sample, you can use the api key '
                           '"special-key" to test '
                           'the authorization filters',
            'license': 'Apache 2.0',
            'licenseUrl': 'http://www.apache.org/licenses/LICENSE-2.0.html',
            'termsOfServiceUrl': 'http://helloreverb.com/terms/',
            'title': 'Swagger Sample App',
        },
        'doc_expansion': 'none',
    },

    # need to set a variable to test that setup was actually run
    # if not run we want to provide a useful error message
    SETUP_STR: True

}
