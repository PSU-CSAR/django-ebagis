FILTER_PREFIX = "FILTER__"

RASTER_TYPECODE = "RasterDataset"
FC_TYPECODE = "FeatureClass"
TABLE_TYPECODE = "Table"

RASTER_EXT = ".img"
FC_EXT = ".shp"
TABLE_EXT = ".dbf"
GDB_EXT = ".gdb"

# Geodatabase Archiving Rule Values
NO_ARCHIVING = 'NONE'
INDIVIDUAL_ARCHIVING = 'INDIVIDUAL'
GROUP_ARCHIVING = 'GROUP'
READ_ONLY = 'READONLY'
ARCHIVING_CHOICES = (
    (NO_ARCHIVING, 'No Archiving'),
    (INDIVIDUAL_ARCHIVING, 'Individual Archiving'),
    (GROUP_ARCHIVING, 'Group Archiving'),
    (READ_ONLY, 'Read Only (No Archiving)'),
)


# HRUZones Directory Name from AOI Directory Structure
ZONES_DIR_NAME = "zones"
HRU_PARAM_GDB_NAME = "param"
HRU_LOG_FILE = "log.xml"

HRU_GDB_LAYERS_TO_SAVE = {RASTER_TYPECODE: ("grid", ),
                          FC_TYPECODE: ("grid_v", "grid_zones_v")}


# aoi gdb names, required layers, and optional layers
REQUIRED_LAYERS = {}
#OPTIONAL_LAYERS = {}

AOI_GDB = "aoi.gdb"
AOI_RASTER_LAYER = (["aoi", "aoibagis"], RASTER_TYPECODE)
REQUIRED_LAYERS[AOI_GDB] = [("aoi_v", FC_TYPECODE),
                            ("aoib", RASTER_TYPECODE),
                            ("aoib_v", FC_TYPECODE),
                            ("p_aoi", RASTER_TYPECODE),
                            ("p_aoi_v", FC_TYPECODE),
                            ("pourpoint", FC_TYPECODE)
                            ]

SURFACES_GDB = "surfaces.gdb"
REQUIRED_LAYERS[SURFACES_GDB] = [("aspect", RASTER_TYPECODE),
                                 #("dem", RASTER_TYPECODE),
                                 ("dem_filled", RASTER_TYPECODE),
                                 ("flow_accumulation", RASTER_TYPECODE),
                                 ("flow_direction", RASTER_TYPECODE),
                                 #("hillshade", RASTER_TYPECODE),
                                 ("slope", RASTER_TYPECODE)
                                 ]

LAYERS_GDB = "layers.gdb"
REQUIRED_LAYERS[LAYERS_GDB] = []

ANALYSIS_GDB = "analysis.gdb"
REQUIRED_LAYERS[ANALYSIS_GDB] = []

PRISM_GDB = "prism.gdb"
REQUIRED_LAYERS[PRISM_GDB] = [("Jan", RASTER_TYPECODE),
                              ("Feb", RASTER_TYPECODE),
                              ("Mar", RASTER_TYPECODE),
                              ("Apr", RASTER_TYPECODE),
                              ("May", RASTER_TYPECODE),
                              ("Jun", RASTER_TYPECODE),
                              ("Jul", RASTER_TYPECODE),
                              ("Aug", RASTER_TYPECODE),
                              ("Sep", RASTER_TYPECODE),
                              ("Oct", RASTER_TYPECODE),
                              ("Nov", RASTER_TYPECODE),
                              ("Dec", RASTER_TYPECODE),
                              ("Q1", RASTER_TYPECODE),
                              ("Q2", RASTER_TYPECODE),
                              ("Q3", RASTER_TYPECODE),
                              ("Q4", RASTER_TYPECODE),
                              ("Annual", RASTER_TYPECODE)]


# name of layer from which to get postgis geometry
AOI_BOUNDARY_LAYER = "aoi_v"

# directory names
ZONES_DIR_NAME = "zones"
MAPS_DIR_NAME = "maps"
PRISM_DIR_NAME = "prism"
