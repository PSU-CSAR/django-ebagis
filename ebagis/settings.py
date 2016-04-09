from __future__ import absolute_import
import os
from datetime import timedelta
from django.conf import settings

from .exceptions import ebagisError
from .initialize import SETUP_STR


# Path where AOI files will be stored
DEFAULT_AOI_DIRECTORY = r'AOIs'
AOI_DIRECTORY = getattr(settings, 'EBAGIS_AOI_DIRECTORY',
                        DEFAULT_AOI_DIRECTORY)

# Path where AOI and download zips will be temporarily stored unzipped
DEFAULT_TEMP_DIRECTORY = None
TEMP_DIRECTORY = getattr(settings, 'EBAGIS_TEMP_DIRECTORY',
                         DEFAULT_TEMP_DIRECTORY)

# Path where download files will be stored
DEFAULT_UPLOADS_DIRECTORY = os.path.join(
    settings.MEDIA_ROOT, "uploads", "%Y", "%m", "%d"
)
UPLOADS_DIRECTORY = getattr(settings, 'EBAGIS_UPLOADS_DIRECTORY',
                            DEFAULT_UPLOADS_DIRECTORY)

# Path where download files will be stored
DEFAULT_DOWNLOADS_DIRECTORY = os.path.join(settings.MEDIA_ROOT, r'downloads')
DOWNLOADS_DIRECTORY = getattr(settings, 'EBAGIS_DOWNLOADS_DIRECTORY',
                              DEFAULT_DOWNLOADS_DIRECTORY)

# Download Expiration Time
DEFAULT_EXPIRATION_DELTA = timedelta(days=1)
EXPIRATION_DELTA = getattr(settings, 'EBAGIS_DOWNLOAD_EXPIRATION_DELTA',
                           DEFAULT_EXPIRATION_DELTA)

# Reference System Well-known ID for geo fields
DEFAULT_GEO_WKID = 4326
GEO_WKID = getattr(settings, 'EBAGIS_GEO_WKID',
                   DEFAULT_GEO_WKID)

# Conf Files
CONF_DIR = getattr(settings, "EBAGIS_CONF_DIR", r"C:\ebagis")
DESKTOP_SETTINGS = getattr(settings, "EBAGIS_DESKTOP_SETTINGS",
                           os.path.join(CONF_DIR, "desktop_settings.yaml"))
LAYER_FILE = getattr(settings, "EBAGIS_LAYER_FILE",
                     os.path.join(CONF_DIR, "BAGIS_Reference_Maps.lyr"))

# Test to make sure setup was run; if run, then SETUP_STR will be True
if not getattr(settings, SETUP_STR, False):
    raise ebagisError(
        "In your settings.py you need to import and call ebagis.settings.setup"
    )
