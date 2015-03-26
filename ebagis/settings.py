from django.conf import settings


# Path where AOI files will be stored
DEFAULT_AOI_DIRECTORY = 'AOIs/'
AOI_DIRECTORY = getattr(settings, 'EBAGIS_AOI_DIRECTORY',
                        DEFAULT_AOI_DIRECTORY)

# Path where AOI zips will be temporarily unzipped
DEFAULT_TEMP_DIRECTORY = None
TEMP_DIRECTORY = getattr(settings, 'EBAGIS_TEMP_DIRECTORY',
                         DEFAULT_TEMP_DIRECTORY)
