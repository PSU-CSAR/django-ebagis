from contextlib import contextmanager


class SpatialReferenceError(Exception):
    pass


def random_string(length=5):
    """
    Returns a string of random letters (uppercase and lowercase) and numbers of
    length specified by the optional length argument. Defualt string length is
    5.
    """
    import string
    import random
    return ''.join(random.choice(string.ascii_letters +
                                 string.digits) for i in xrange(length))


def make_short_name(name, maxlength=15):
    """
    Take a string (name), replace spaces with _, and return result less than a
    maximum length, defined by the optional maxlength parameter. Defualt is max
    length of 15 characters.
    """
    nospaces = "_".join(name.split())

    length = len(nospaces)
    if length > maxlength:
        length = maxlength

    return nospaces[:length]


def generate_random_name(layershortname, ext=""):
    return layershortname + "_" + random_string() + ext


def get_pg_srid(psycopgcursor, spatialref, test="WKT"):
    """
    """
    if test == "WKT":
        getref = spatialref.ExportToWkt
    elif test == "PROJ4":
        getref = spatialref.ExportToProj4

    psycopgcursor.execute("SELECT srid FROM spatial_ref_sys WHERE srtext ILIKE '{}'".format(getref()))
    result = psycopgcursor.fetchall()

    if len(result) == 1:
        return result[0][0]
    else:
        return None


def srid_of_spatialref(psycopgcursor, spatialref):
    """
    """
    srid = None#get_pg_srid(psycopgcursor, spatialref, test="WKT")

    if not srid:
        srid = get_pg_srid(psycopgcursor, spatialref, test="PROJ4")

    if not srid:
        raise SpatialReferenceError("Unable to determine srid of spatial reference.")

    return srid


def get_multipart_wkt_geometry(sourcefile, layername=None):
    """
    """
    from osgeo import ogr

    ogr.UseExceptions()

    # open sourcefile using OGR
    shapefile = ogr.Open(sourcefile)

    if not shapefile:
        raise Exception("Failed to open file {}.".format(sourcefile))

    if layername:
        layer = shapefile.GetLayerByName(layername)
    else:
        layer = shapefile.GetLayer(0)

    crs_wkt = layer.GetSpatialRef().ExportToWkt()

    # iterate through features in shapefile, getting geometry as WKT
    geometries = []

    # shapefiles start feature indicies at 0, but geodatabase seems
    # to start a 1; using a while loop to allow skipping indicies within
    # the feature count range that do not return a feature
    i = 0
    while i <= layer.GetFeatureCount():
        try:
            feature = layer.GetFeature(i)
            wkt = feature.GetGeometryRef().ExportToWkt()
            geometries.append(wkt)
        except AttributeError:
            pass
        except RuntimeError:
            pass
        i += 1

    feature = None
    layer = None
    shapefile = None

    return (wkt_polygons_to_multipolygon(geometries), crs_wkt)


def wkt_polygons_to_multipolygon(wkt_polygons):
    cleaned_wkts = []

    for wkt in wkt_polygons:
        # remove individual geometry types to allow merging into multipolygon
        if wkt.startswith("POLYGON"):
            wkt = wkt[8:]
        elif wkt.startswith("MULTIPOLYGON"):
            wkt = wkt[14:-1]
        else:
            raise Exception("Invalid or unknown geometry type detected.")

        cleaned_wkts.append(wkt)

    return "MULTIPOLYGON (" + ",".join(cleaned_wkts) + ")"


def reproject_wkt(wkt, src_crs, dst_crs):
    from osgeo import ogr, osr
    tf = osr.CoordinateTransformation(src_crs, dst_crs)
    geom = ogr.CreateGeometryFromWkt(wkt)
    geom.Transform(tf)
    return geom.ExportToWkt()


def get_authority_code_from_spatial_ref(spatial_ref):
    return spatial_ref.GetAttrValue("AUTHORTIY", 1)


def create_spatial_ref_from_EPSG(epsg_code):
    """
    """
    from osgeo import osr
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(epsg_code)
    return spatial_ref


def create_spatial_ref_from_wkt(wkt):
    """
    """
    from osgeo import osr
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromWkt(wkt)
    return spatial_ref


def get_seq_next_val(connection, sequence):
    with connection.cursor() as cursor:
            cursor.execute("SELECT nextval('{}');".format(sequence))
            return cursor.fetchall()[0][0]


def make_unique_directory(shortname, data_repository):
    import os

    while True:
        uniqueid = shortname + "_" + random_string()
        outdirectory = os.path.join(data_repository, uniqueid)

        try:
            os.mkdir(outdirectory)
            break
        except OSError:
            pass

    return uniqueid, outdirectory


def validate_path(path, allow_whitespace=False,
                  invalid_chars=[":", "/", "\\", "*", "?", ".", "%", "$"]):
    if not allow_whitespace:
        from string import whitespace
        for char in whitespace:
            if char in path:
                raise Exception("Cannot contain whitespace.")

    for char in invalid_chars:
        if char in path:
            raise Exception(
                "Cannot contain {}.".format(invalid_chars)
            )

    return path


def zip_directory(directory_path, zip_path):
    import os
    import zipfile
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for f in files:
                rel_dir = os.path.relpath(root, directory_path)
                # first arg is file to zip, second arg is archive name
                # (second arg is path realtive to the root of the AOI
                # to keep whole higher level directory structure from
                # getting zipped)
                zipf.write(os.path.join(root, f), os.path.join(rel_dir, f))
            # NEED TO USE THIS FOR EMPTY DIRS
            #for d in dirs:
              #  zips.writestr(zipfile.ZipInfo('empty/'), '')
    return zip_path


@contextmanager
def tempdirectory(suffix="", prefix="", dir=None):
    """A context manager for creating and then
    deleting a temporary directory.
    """
    from tempfile import mkdtemp
    from shutil import rmtree
    tmpdir = mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    try:
        yield tmpdir
    except Exception as e:
        raise e
    finally:
        rmtree(tmpdir)
        pass
