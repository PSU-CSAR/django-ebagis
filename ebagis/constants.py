URL_FILTER_QUERY_ARG_PREFIX = "FILTER__"

RASTER_TYPECODE = "RasterDataset"
FC_TYPECODE = "FeatureClass"
TABLE_TYPECODE = "Table"

RASTER_EXT = ".img"
FC_EXT = ".shp"
TABLE_EXT= ".dbf"

# Geodatabase Archiving Rule Values
NO_ARCHIVING = 'NONE'
LAYER_ARCHIVING = 'LAYER'
GROUP_ARCHIVING = 'GROUP'
ARCHIVING_CHOICES = (
    (NO_ARCHIVING, 'No Archiving'),
    (LAYER_ARCHIVING, 'Layer Archiving'),
    (GROUP_ARCHIVING, 'Group Archiving'),
)