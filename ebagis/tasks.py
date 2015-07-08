from __future__ import absolute_import
from celery import shared_task
import os
import shutil

from logging import exception

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import transaction

import arcpy

from .constants import AOI_RASTER_LAYER, AOI_GDB, REQUIRED_LAYERS

from .exceptions import AOIError

from .models.aoi import AOI

# Geodatabase Classes
from .models.geodatabase import AOIdb, Surfaces, Layers, Prism, Analysis

# Layer/File Classes
from .models.file import Raster, Vector, XML, Table
from .models.file_data import RasterData, VectorData, TableData, XMLData

# Directory Classes
from .models.directory import Maps

from .models.upload import AOIUpload
from .models.download import Download

from arcpy_extensions.geodatabase import Geodatabase

from .utilities import make_short_name, get_multipart_wkt_geometry,\
    tempdirectory, create_spatial_ref_from_EPSG, reproject_wkt,\
    get_authority_code_from_spatial_ref, create_spatial_ref_from_wkt,\
    validate_path, zip_directory

from .serializers import AOIListSerializer

from .settings import AOI_DIRECTORY, TEMP_DIRECTORY, GEO_WKID,\
    DOWNLOADS_DIRECTORY


# ************ FUNCTIONS **************

def import_gdb(temp_aoi_path, geodatabase_name, GDBClass, user, aoi):
    """
    """
    # get this GDB's content type
    gdb_content_type = ContentType.objects.get_for_model(GDBClass, for_concrete_model=False)
    raster_content_type = ContentType.objects.get_for_model(Raster, for_concrete_model=False)
    vector_content_type = ContentType.objects.get_for_model(Vector, for_concrete_model=False)
    table_content_type = ContentType.objects.get_for_model(Table, for_concrete_model=False)

    # create the django gdb object
    gdb_obj = GDBClass(aoi=aoi, name=GDBClass.__name__)
    gdb_obj.save()

    created_at = gdb_obj.created_at.strftime("_%Y%m%d%H%M%S")
    output_dir = gdb_obj.directory_path

    # get all geodatabase layers and copy to outdirectory
    gdb = Geodatabase.open_GDB(os.path.join(temp_aoi_path, geodatabase_name))

    # copy rasters and create raster and raster data objects
    for raster in gdb.rasterlayers:
        outraster = gdb.raster_layer_to_file(raster, output_dir,
                                             outname_to_use=raster+created_at)
        desc = arcpy.Describe(outraster)
        raster_layer = Raster(name=raster,
                              object_id=gdb_obj.id,
                              content_type=gdb_content_type,
                              aoi=aoi)
        raster_layer.save()
        RasterData(filename=raster,
                   filepath=outraster,
                   object_id=raster_layer.id,
                   content_type=raster_content_type,
                   #srs_wkt=desc.spatialReference.exportToString(),
                   #resolution=desc.meanCellWidth,
                   created_by=user,
                   aoi=aoi).save()

    # copy vectors and create vector and vetor data objects
    for vector in gdb.featureclasses:
        outvector = gdb.feature_class_to_shapefile(
            vector, output_dir, outname_to_use=vector+created_at
        )
        desc = arcpy.Describe(outvector)
        vector_layer = Vector(name=vector,
                              object_id=gdb_obj.id,
                              content_type=gdb_content_type,
                              aoi=aoi)
        vector_layer.save()
        VectorData(filename=vector,
                   filepath=outvector,
                   object_id=vector_layer.id,
                   content_type=vector_content_type,
                   #srs_wkt=desc.spatialReference.exportToString(),
                   #geom_type=desc.shapeType,
                   created_by=user,
                   aoi=aoi).save()

    # copy tables and create table and table data objects
    for table in gdb.tables:
        outtable = gdb.table_to_file(table, output_dir,
                                     outname_to_use=table+created_at)
        desc = arcpy.Describe(outtable)
        table_layer = Table(name=table,
                            object_id=gdb_obj.id,
                            content_type=gdb_content_type,
                            aoi=aoi)
        table_layer.save()
        TableData(filename=table,
                  filepath=outtable,
                  object_id=table_layer.id,
                  content_type=table_content_type,
                  created_by=user,
                  aoi=aoi).save()

    return gdb_obj


@transaction.atomic
def import_aoi(temp_aoi_path, aoi_name, aoi_shortname, user):
    """
    """
    try:
        # get multipolygon WKT from AOI Boundary Layer
        wkt, crs_wkt = get_multipart_wkt_geometry(os.path.join(temp_aoi_path,
                                                               AOI_GDB),
                                                  layername=AOI_BOUNDARY_LAYER)

        crs = create_spatial_ref_from_wkt(crs_wkt)

        if get_authority_code_from_spatial_ref(crs) != GEO_WKID:
            dst_crs = create_spatial_ref_from_EPSG(GEO_WKID)
            wkt = reproject_wkt(wkt, crs, dst_crs)

        aoi = AOI(name=aoi_name,
                  shortname=aoi_shortname,
                  boundary=wkt,
                  created_by=user)

        aoi.save()

        # TODO: convert GDB imports to use celery group or multiprocessing
        # import aoi.gdb
        aoi.aoidb = import_gdb(temp_aoi_path, AOI_GDB, AOIdb, user, aoi)
        aoi.save()

        # import surfaces.gdb
        aoi.surfaces = import_gdb(temp_aoi_path, SURFACES_GDB,
                                  Surfaces, user, aoi)
        aoi.save()

        # import layers.gdb
        aoi.layers = import_gdb(temp_aoi_path, LAYERS_GDB,
                                Layers, user, aoi)
        aoi.save()

        # import HRU GDBs in zones/

        # import analysis.gdb
        aoi.analysis = import_gdb(temp_aoi_path, ANALYSIS_GDB,
                                  Analysis, user, aoi)
        aoi.save()

        # import prism.gdb
        aoi.prism.add(import_gdb(temp_aoi_path, PRISM_GDB, Prism, user, aoi))
        aoi.save()

        # import param.gdb

        # import loose files in param/

        # import param/paramdata.gdb

        # import map docs in maps directory
        maps = Maps(aoi=aoi, name=Maps.__name__)
        maps.save()
        aoi.maps = maps
        aoi.save()
    except Exception as e:
        try:
            if aoi.directory_path:
                shutil.rmtree(aoi.directory_path)
        except:
            exception("Failed to remove AOI directory on import error.")
        raise e

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
                    if not arcpy.Describe(
                        os.path.join(gdb_path,
                                     layer)
                    ).DataType == layertype:
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
                if filename.startswith("/") or \
                        filename.startswith("\\") or ".." in filename:
                    raise BadZipfile("AOI zipfile contains nonstandard" +
                                     " filenames and cannot be opened.")

        zfile.extractall(path=unzipdir)


def validate_shortname(shortname):
    validate_path(shortname)
    return shortname


def extract_and_import_aoi(aoi_zip_path, aoi_name, aoi_shortname, user):
    with tempdirectory(prefix="AOI_", dir=TEMP_DIRECTORY) as tempdir:
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

        #return import_aoi(temp_aoi_path, aoi_name, aoi_shortname, user)

        return AOI.create(aoi_name, aoi_shortname, user, temp_aoi_path)


@shared_task
def add_aoi(aoiupload_id):

    aoiupload = AOIUpload.objects.get(pk=aoiupload_id)

    aoi_name = os.path.splitext(aoiupload.filename)[0]
    aoi_shortname = make_short_name(aoi_name)
    user = aoiupload.user
    aoi_zip_path = aoiupload.file

    aoi = extract_and_import_aoi(aoi_zip_path, aoi_name,
                                 aoi_shortname, user)

    return aoi.id


def add_aoi_manually(aoi_zip_path, aoi_name, user_id, aoi_shortname=None):

    if not aoi_name:
        raise AOIError("Required argument AOI Name was not specified.")

    if aoi_shortname:
        validate_shortname(aoi_shortname)
    else:
        aoi_shortname = make_short_name(aoi_name)

    user = User.objects.get(pk=user_id)

    extract_and_import_aoi(aoi_zip_path, aoi_name, aoi_shortname, user)


@shared_task
def export_data(download_id):
    download = Download.objects.get(pk=download_id)
    out_dir = os.path.join(DOWNLOADS_DIRECTORY, download_id)
    os.makedirs(out_dir)

    print download.querydate

    with tempdirectory(prefix="AOI_", dir=TEMP_DIRECTORY) as tempdir:
        temp_aoi_dir = download.content_object.export(
            tempdir,
            querydate=download.querydate
        )

        zip_dir = os.path.join(out_dir,
                               os.path.basename(temp_aoi_dir) + ".zip")

        download.file = zip_directory(temp_aoi_dir, zip_dir)

    download.save()
    return download.id


#def export_aoi_manually(output_directory, )
