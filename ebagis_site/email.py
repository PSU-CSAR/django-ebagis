_DEFAULT = "_default"

HOST = _DEFAULT
PORT = _DEFAULT
USER = _DEFAULT
PASSWORD = _DEFAULT
SUBJECT_PREFIX = _DEFAULT
USE_SSL = True

# the defaults obviously need to be changed by the user
# raise an exception if they have not been configured
if _DEFAULT in [HOST, PORT, USER, PASSWORD, SUBJECT_PREFIX, USE_SSL]:
    raise Exception("Please edit the values in ebagis_site/email.py.")
