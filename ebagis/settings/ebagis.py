import os
from datetime import timedelta

INSTALLED_APPS += (
    'ebagis',
    'ebagis.data',
)

# Path where AOI files will be stored
AOI_DIRECTORY = os.path.join(BASE_DIR, 'AOIs')

# Path where AOI and download zips will be temporarily stored unzipped
TEMP_DIRECTORY = None

# Path where download files will be stored
UPLOADS_DIRECTORY = os.path.join(
    MEDIA_ROOT, "uploads", "%Y", "%m", "%d"
)

# Path where download files will be stored
DOWNLOADS_DIRECTORY = os.path.join(MEDIA_ROOT, r'downloads')

# Download Expiration Time
EXPIRATION_DELTA = timedelta(days=1)

# Reference System Well-known ID for geo fields
GEO_WKID = 4326

# AWDB Web Service settings
AWDB_QUERY_URL = 'http://localhost/arcgis/rest/services/AWDB_ALL/stations_USGS_ALL/MapServer/0/query'
# note that the search buffer actually turns into a retangular
# search envelope, so take care in setting as not all found points
# may be within the specified distance from the search point
AWDB_SEARCH_BUFFER = "100 Meters"

# Conf Files
CONF_DIR =  r"C:\ebagis"
DESKTOP_SETTINGS = os.path.join(CONF_DIR, "desktop_settings.yaml")
LAYER_FILE = os.path.join(CONF_DIR, "BAGIS_Reference_Maps.lyr")
