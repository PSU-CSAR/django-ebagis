from __future__ import absolute_import
from celery import shared_task
import os

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import transaction

import arcpy

from .constants import RASTER_EXT, FC_EXT, TABLE_EXT

# Geodatabase Classes
from .models import AOI, AOIdb, Surfaces, Layers, Prism, Analysis, HRUZones

# Layer/File Classes
from .models import Raster, Vector, XML, Table

# Directory Classes
from .models import Maps, CRS_WKID

from .models import AOIUpload

from arcpy_extensions.constants import RASTER_TYPECODE, FC_TYPECODE,\
    TABLE_TYPECODE
from arcpy_extensions.geodatabase import Geodatabase

from .utilities import make_short_name, get_multipart_wkt_geometry,\
    tempdirectory, create_spatial_ref_from_EPSG, reproject_wkt,\
    get_authority_code_from_spatial_ref, create_spatial_ref_from_wkt,\
    validate_path

from .serializers import AOIListSerializer


AOIS_ROOT = r"D:\projects\ebagis\DatabaseInterfaceTesting\AOIs\ebagis"
TEMP_DIRECTORY = r"D:\projects\ebagis\DatabaseInterfaceTesting\AOIs\temp"

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
REQUIRED_LAYERS[PRISM_GDB] = [('Jan', RASTER_TYPECODE),
                              ('Feb', RASTER_TYPECODE),
                              ('Mar', RASTER_TYPECODE),
                              ('Apr', RASTER_TYPECODE),
                              ('May', RASTER_TYPECODE),
                              ('Jun', RASTER_TYPECODE),
                              ('Jul', RASTER_TYPECODE),
                              ('Aug', RASTER_TYPECODE),
                              ('Sep', RASTER_TYPECODE),
                              ('Oct', RASTER_TYPECODE),
                              ('Nov', RASTER_TYPECODE),
                              ('Dec', RASTER_TYPECODE),
                              ('Q1', RASTER_TYPECODE),
                              ('Q2', RASTER_TYPECODE),
                              ('Q3', RASTER_TYPECODE),
                              ('Q4', RASTER_TYPECODE),
                              ('Annual', RASTER_TYPECODE)]


# name of layer from which to get postgis geometry
AOI_BOUNDARY_LAYER = "aoi_v"

# directory names
ZONES_NAME = "Zones"
MAPS_NAME = "Maps"


class AOIError(Exception):
    pass


# ************ FUNCTIONS **************

def import_gdb(temp_aoi_path, aoi_dir, geodatabase_name, GDBClass, user, aoi):
    """
    """
    # get this GDB's content type
    content_type = ContentType.objects.get_for_model(GDBClass)

    # create directory in aoi_dir for aoi gdb layers
    output_dir = os.path.join(aoi_dir, os.path.splitext(geodatabase_name)[0])
    try:
        os.mkdir(output_dir)
    except:
        raise AOIError("Failed to create the {} gdb directory."
                       .format(os.path.splitext(geodatabase_name)[0]))

    # create the django gdb object
    gdb_obj = GDBClass(aoi=aoi, name=GDBClass.__name__, created_by=user)
    gdb_obj.save()

    created_at = gdb_obj.created_at.strftime("_%Y%m%d%H%M%S")

    # get all geodatabase layers and copy to outdirectory
    gdb = Geodatabase.open_GDB(os.path.join(temp_aoi_path, geodatabase_name))

    # copy rasters and create raster objects
    for raster in gdb.rasterlayers:
        outraster = gdb.raster_layer_to_file(raster, output_dir,
                                             outname_to_use=raster+created_at)
        desc = arcpy.Describe(outraster)
        Raster(name=raster,
               filename=outraster,
               object_id=gdb_obj.id,
               content_type=content_type,
               srs_wkt=desc.spatialReference.exportToString(),
               resolution=desc.meanCellWidth,
               created_by=user,
               aoi=aoi).save()

    # copy vectors and create vector objects
    for vector in gdb.featureclasses:
        outvector = gdb.feature_class_to_shapefile(
            vector, output_dir, outname_to_use=vector+created_at
        )
        desc = arcpy.Describe(outvector)
        Vector(name=vector,
               filename=outvector,
               object_id=gdb_obj.id,
               content_type=content_type,
               srs_wkt=desc.spatialReference.exportToString(),
               geom_type=desc.shapeType,
               created_by=user,
               aoi=aoi).save()

    # copy tables and create table objects
    for table in gdb.tables:
        outtable = gdb.table_to_file(table, output_dir,
                                     outname_to_use=table+created_at)
        desc = arcpy.Describe(outtable)
        Table(name=table,
              filename=outtable,
              object_id=gdb_obj.id,
              content_type=content_type,
              created_by=user,
              aoi=aoi).save()

    return gdb_obj


@transaction.atomic
def import_aoi(temp_aoi_path, aoi_name, aoi_shortname, user):
    """
    """
    # make AOI directory in AOIS_ROOT
    aoi_dir = os.path.join(AOIS_ROOT, aoi_name)
    try:
        os.makedirs(aoi_dir)
    except Exception as e:
        print e
        raise AOIError("Failed to create AOI directory on server.")

    # get multipolygon WKT from AOI Boundary Layer
    wkt, crs_wkt = get_multipart_wkt_geometry(os.path.join(temp_aoi_path,
                                                           AOI_GDB),
                                              layername=AOI_BOUNDARY_LAYER)

    crs = create_spatial_ref_from_wkt(crs_wkt)

    if get_authority_code_from_spatial_ref(crs) != CRS_WKID:
        dst_crs = create_spatial_ref_from_EPSG(CRS_WKID)
        wkt = reproject_wkt(wkt, crs, dst_crs)

    aoi = AOI(name=aoi_name,
              shortname=aoi_shortname,
              boundary=wkt,
              directory_path=aoi_dir,
              created_by=user)

    aoi.save()

    # TODO: convert GDB imports to use celery group or multiprocessing
    # import aoi.gdb
    aoi.aoidb = import_gdb(temp_aoi_path, aoi_dir, AOI_GDB, AOIdb, user, aoi)
    aoi.save()

    # import surfaces.gdb
    aoi.surfaces = import_gdb(temp_aoi_path, aoi_dir, SURFACES_GDB,
                              Surfaces, user, aoi)
    aoi.save()

    # import layers.gdb
    aoi.layers = import_gdb(temp_aoi_path, aoi_dir, LAYERS_GDB,
                            Layers, user, aoi)
    aoi.save()

    # import HRU GDBs in zones/

    # import analysis.gdb
    aoi.analysis = import_gdb(temp_aoi_path, aoi_dir, ANALYSIS_GDB,
                              Analysis, user, aoi)
    aoi.save()

    # import prism.gdb
    aoi.prism = import_gdb(temp_aoi_path, aoi_dir, PRISM_GDB, Prism, user, aoi)
    aoi.save()

    # import param.gdb

    # import loose files in param/

    # import param/paramdata.gdb

    # import map docs in maps directory
    try:
        os.mkdir(os.path.join(aoi_dir, MAPS_NAME))
    except:
        raise AOIError("Failed to create Maps directory.")

    maps = Maps(aoi=aoi, created_by=user, name=Maps.__name__)
    maps.save()

    aoi.save()

    return aoi


def validate_required_gdb_layers(gdb_path, required_layers):
    """
    """
    errorlist = []

    if not arcpy.Exists(gdb_path):
        errorlist.append("Geodatabase {} does not exist in AOI."
                         .format(os.path.basename(gdb_path)))
    else:
        if required_layers:
            for layer, layertype in required_layers:
                try:
                    if not arcpy.Describe(os.path.join(gdb_path,
                                                layer)).DataType == layertype:
                        errorlist.append(
                            "Layer {} is not required type {}.".format(
                                os.path.join(os.path.basename(gdb_path),
                                             layer),
                                layertype
                                )
                        )
                except IOError:
                    errorlist.append(
                        "Layer {} was not found.".format(
                            os.path.join(os.path.basename(gdb_path), layer)
                            )
                    )

    return errorlist


def validate_aoi(aoi_path):
    """
    """
    errorlist = []

    # check to see that path is valid
    if not arcpy.Exists(aoi_path):
        errorlist.append("AOI path is not valid.")
        return errorlist

    # check for aoi boundary raster layer
    # must be separate as multiple names possible
    found = False
    for layer in AOI_RASTER_LAYER[0]:
        try:
            found = found or (arcpy.Describe(
                os.path.join(aoi_path, AOI_GDB, layer))
                .DataType == AOI_RASTER_LAYER[1])
        except IOError:
            pass

    if not found:
        errorlist.append("Raster AOI boundary was not found."
                         .format(os.path.join(os.path.basename(aoi_path),
                                              AOI_GDB,
                                              layer)))

    # check for required gdbs and their required layers
    for gdb, required_layers in REQUIRED_LAYERS.iteritems():
        errorlist += validate_required_gdb_layers(os.path.join(aoi_path, gdb),
                                                  required_layers)

    return errorlist


def get_aoi_path_from_tempdir(tempdir):
    tempdircontents = os.listdir(tempdir)

    directories = []
    for item in tempdircontents:
        item = os.path.join(tempdir, item)
        if os.path.isdir(item):
            directories.append(item)

    if len(directories) == 1:
        aoi_path = directories[0]
    else:
        aoi_path = tempdir

    return aoi_path


def unzip_AOI(aoizip, unzipdir):
    """
    """
    from zipfile import ZipFile, BadZipfile

    with ZipFile(aoizip) as zfile:
        files = zfile.namelist()

        # ensure zipfile integrity
        if zfile.testzip():
            raise BadZipfile("AOI zipfile has errors." +
                             " Please try resubmitting your request.")

        # validate zfile members: make sure no problem char in names
        if not files:
            raise BadZipfile("AOI zipfile is empty.")
        else:
            for filename in files:
                if filename.startswith("/") or filename.startswith("\\") or ".." in filename:
                    raise BadZipfile("AOI zipfile contains nonstandard" +
                                     " filenames and cannot be opened.")

        zfile.extractall(path=unzipdir)


def validate_shortname(shortname):
    validate_path(shortname)
    return shortname


@shared_task
def add_aoi(aoiupload_id):

    aoiupload = AOIUpload.objects.get(pk=aoiupload_id)

    aoi_name = os.path.splitext(aoiupload.filename)[0]
    aoi_shortname = make_short_name(aoi_name)
    user = aoiupload.user
    aoi_zip_path = aoiupload.file

    with tempdirectory(prefix="AOI_") as tempdir:
        print "Extracting AOI to {}.".format(tempdir)
        unzip_AOI(aoi_zip_path, tempdir)

        temp_aoi_path = get_aoi_path_from_tempdir(tempdir)

        print "AOI to import is {}.".format(temp_aoi_path)

        aoi_errors = validate_aoi(temp_aoi_path)

        if aoi_errors:
            errormsg = "Errors were encountered with the AOI {}:"\
                                                     .format(temp_aoi_path)
            for error in aoi_errors:
                errormsg += "\n\t{}".format(error)
            raise AOIError(errormsg)

        aoi = import_aoi(temp_aoi_path, aoi_name, aoi_shortname, user)

    return aoi.id


def add_aoi_manually(aoi_zip_path, aoi_name, user_id, aoi_shortname=None):

    if not aoi_name:
        raise AOIError("Required argument AOI Name was not specified.")

    if aoi_shortname:
        validate_shortname(aoi_shortname)
    else:
        aoi_shortname = make_short_name(aoi_name)

    user = User.objects.get(pk=user_id)

    with tempdirectory(prefix="AOI_") as tempdir:
        print "Extracting AOI to {}.".format(tempdir)
        unzip_AOI(aoi_zip_path, tempdir)

        temp_aoi_path = get_aoi_path_from_tempdir(tempdir)

        print "AOI to import is {}.".format(temp_aoi_path)

        aoi_errors = validate_aoi(temp_aoi_path)

        if aoi_errors:
            errormsg = "Errors were encountered with the AOI {}:"\
                                                       .format(temp_aoi_path)
            for error in aoi_errors:
                errormsg += "\n\t{}".format(error)
            raise AOIError(errormsg)

        import_aoi(temp_aoi_path, aoi_name, aoi_shortname, user)
