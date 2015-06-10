import os
from datetime import timedelta
from django.conf import settings


# Path where AOI files will be stored
DEFAULT_AOI_DIRECTORY = r'AOIs'
AOI_DIRECTORY = getattr(settings, 'EBAGIS_AOI_DIRECTORY',
                        DEFAULT_AOI_DIRECTORY)

# Path where AOI and download zips will be temporarily stored unzipped
DEFAULT_TEMP_DIRECTORY = None
TEMP_DIRECTORY = getattr(settings, 'EBAGIS_TEMP_DIRECTORY',
                         DEFAULT_TEMP_DIRECTORY)

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
