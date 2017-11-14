INSTALLED_APPS += (
    'rest_framework',
    'rest_framework_gis',
    'rest_framework_swagger',
    'drf_chunked_upload',
)

# defined api versions
api_versions = [0.1, 0.2]

REST_FRAMEWORK = {
    # user authentication
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'ebagis.authentication.ExpiringTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        ),
    'DEFAULT_PERMISSION_CLASSES': (
        'ebagis.permissions.CheckAdminStaffAuthOrAnon',
        #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        #'rest_framework.permissions.IsAdminUser',
        ),
    'PAGINATE_BY': 100,
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ),
    'DEFAULT_VERSIONING_CLASS':
        'rest_framework.versioning.AcceptHeaderVersioning',
    'ALLOWED_VERSIONS': [str(x) for x in api_versions],
    'DEFAULT_VERSION': str(max(api_versions)),
}

SWAGGER_SETTINGS = {
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
}
