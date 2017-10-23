import os

# logging settings
MAX_LENGTH = 5 * 1024 * 1024  # 50 MB
MAX_FILES = 10


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt': "%d/%b/%Y %H:%M:%S",
        },
        'simple': {
            'format': '%(asctime)s %(name)s [%(levelname)s] %(message)s',
            'datefmt': "%d/%b/%Y %H:%M:%S",
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'formatter': 'verbose',
            'maxBytes': MAX_LENGTH,
            'backupCount': (MAX_FILES - 1),
        },
        'celery': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'celery.log'),
            'formatter': 'simple',
            #'maxBytes': 1024 * 1024 * 5,  # 5 mb
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['celery'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'ebagis': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'drf_chunked_upload': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    },
}
