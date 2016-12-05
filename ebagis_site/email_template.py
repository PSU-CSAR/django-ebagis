## EMAIL SETTINGS ##
## uncomment each and provide a value as required for your application
## each value pre-populated with the default, where possible


## The backend to use for sending emails.
## For the list of available backends see
## https://docs.djangoproject.com/en/1.9/topics/email/#email-backends

#EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"


## The directory used by the file email backend to store output files.
## Default: Not defined

#EMAIL_FILE_PATH = ""


## The host to use for sending email.
## Either IP address or DNS name.

#EMAIL_HOST = "localhost"


## Port to use for the SMTP server defined in EMAIL_HOST.

#EMAIL_PORT = 25


## Username to use for the SMTP server defined in EMAIL_HOST.
## If either of these settings is empty, Django won’t attempt authentication.

#EMAIL_HOST_USER = ""


## Password to use for the SMTP server defined in EMAIL_HOST.
##This setting is used in conjunction with EMAIL_HOST_USER
## when authenticating to the SMTP server.
## If either of these settings is empty, Django won’t attempt authentication.

#EMAIL_HOST_PASSWORD = ""


## Subject-line prefix for email messages sent with
## django.core.mail.mail_admins or django.core.mail.mail_managers.
## You’ll probably want to include the trailing space.

#EMAIL_SUBJECT_PREFIX = "[Django] "


## Whether to use a TLS (secure) connection when talking
## to the SMTP server. This is used for explicit TLS connections,
## generally on port 587. If you are experiencing hanging
## connections, see the implicit TLS setting EMAIL_USE_SSL.
## Note that EMAIL_USE_TLS/EMAIL_USE_SSL are mutually exclusive,
## so only set one of those settings to True.

#EMAIL_USE_TLS = False


## Whether to use an implicit TLS (secure) connection
## when talking to the SMTP server. In most email
## documentation this type of TLS connection is referred
## to as SSL. It is generally used on port 465. If you are
## experiencing problems, see the explicit TLS setting
## EMAIL_USE_TLS.
## Note that EMAIL_USE_TLS/EMAIL_USE_SSL are mutually exclusive,
## so only set one of those settings to True.

#EMAIL_USE_SSL = False


## If EMAIL_USE_SSL or EMAIL_USE_TLS is True,
## you can optionally specify the path to a
## PEM-formatted certificate chain file to
## use for the SSL connection.

#EMAIL_SSL_CERTFILE = None


## If EMAIL_USE_SSL or EMAIL_USE_TLS is True,
## you can optionally specify the path to a
## PEM-formatted private key file to use
## for the SSL connection.

#EMAIL_SSL_KEYFILE = None


## Specifies a timeout in seconds for
## blocking operations like the connection attempt.

#EMAIL_TIMEOUT = None


## Default email address to use for various automated
## correspondence from the site manager(s).
## This doesn’t include error messages sent to ADMINS and MANAGERS;
## for that, see SERVER_EMAIL.

#DEFAULT_FROM_EMAIL = "webmaster@localhost"
