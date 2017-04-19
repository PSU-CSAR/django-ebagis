INSTALLED_APPS += (
    'djcelery',
)

import djcelery
djcelery.setup_loader()

# celery settings
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYD_CONCURRENCY = 4

BROKER_URL = 'amqp://{name}:{pw}@localhost:5672/{name}'.format(
    name=CELERY_BROKER_USER,
    pw=CELERY_BROKER_PASSWORD,
)
