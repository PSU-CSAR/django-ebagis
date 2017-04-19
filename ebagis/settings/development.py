INSTALLED_APPS += (
    'django_extensions',
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

# settings for graphing data model (django-extensions)
GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}