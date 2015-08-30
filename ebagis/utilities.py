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


# I THINK THIS IS DEAD CODE; VERIFY AND REMOVE
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


# I THINK THIS IS DEAD CODE; VERIFY AND REMOVE
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
    """extract a single multipolygon geometry from an sourcefile
    containing polygon geometries"""
    from osgeo import ogr

    ogr.UseExceptions()

    # open sourcefile using OGR
    dataset = ogr.Open(sourcefile)

    if not dataset:
        raise Exception("Failed to open file {}.".format(sourcefile))

    if layername:
        layer = dataset.GetLayerByName(layername)
    else:
        layer = dataset.GetLayer(0)

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
    """put multiple wkt polygons together to form a single
    multipolygon wkt geometry"""
    cleaned_wkts = []

    for wkt in wkt_polygons:
        # remove individual geometry types to allow merging into multipolygon
        if wkt.startswith("POLYGON"):
            wkt = wkt[8:]
        elif wkt.startswith("MULTIPOLYGON"):
            wkt = wkt[14:-1]
        else:
            raise Exception("Invalid or unknown geometry type detected.")

        # append the geometry to this list, sans geometry type tag
        cleaned_wkts.append(wkt)

    # join the individual geometeries in the list into a single multipolygon
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
    from osgeo import osr
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(epsg_code)
    return spatial_ref


def create_spatial_ref_from_wkt(wkt):
    from osgeo import osr
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromWkt(wkt)
    return spatial_ref


def get_seq_next_val(connection, sequence):
    with connection.cursor() as cursor:
            cursor.execute("SELECT nextval('{}');".format(sequence))
            return cursor.fetchall()[0][0]


def generate_postfix(iteration, sequential=False):
    """used to generate the postfixes for the
    make_unique_directory function"""
    # a sequential postfix uses integers
    if sequential:
        postfix = "_" + iteration
    else:
        # otherwise we append a unique string
        # the length of the string is 4 char,
        # but increases by 1 every 100 iterations
        length = 4 + (1 * (iteration % 100))
        postfix = "_" + random_string(length)
    return postfix


def make_unique_directory(name, path,
                          limit=None,
                          sequential_postfix=False,
                          always_append=False):
    """Iterate though postfixes to a directory name until
    the name is unique and the directory can be created. If
    the original name is unique no postfix will be appended,
    unless the always_append option is set to True, in which
    case a postfix will be appended, even if the name was
    already unique.

    User can set a limit value to stop trying to create the
    directory after that many failed attempts. The default is
    to run an unlimited number of times.

    User can also choose to use a sequential postfix, which
    appends an integer to the file name, starting with 1, and
    increments the integer until the limit is reached. Note that
    combining the sequential_postfix and always_append options
    will not start at 1, but at 0. The default behavior is to use
    a random string which is minimally 4 characters. Every 100
    iterations the string will add an extra letter to attempt to
    avoid collisions and make the directory more quickly.

    The two required arguments to this function are name and path,
    which are both strings. Name will be used as the starting point
    for the name of the directory to be created, and path is the
    location at which the directory should be created. That is,
    with a name of `bar` and a path of `/home/foo/`, the function
    will attempt to create the directory `/home/foo/bar`, appending
    a postfix as desribed above until the directory can be created."""
    import os

    # if no limit then set to True so while loop will never stop
    if limit is None:
        limit = True
    # if limit is a postive integer, don't need to do anything
    else if type(limit) == int and limit > 0:
        continue
    # if limit is neither of these then we don't know what to do
    else:
        raise InputError("limit is not positive integer or None. Unable to proceed")

    # postfix starts as empty string unless always_append is True
    postfix = ""
    if always_append is True:
        postfix = generate_postfix(0, sequential_postfix)

    # iterate through names until directory is created
    while limit:
        iteration += 1

        # append postfix and create full directory path
        uniqueid = name + postfix
        outdirectory = os.path.join(data_repository, uniqueid)

        # if the directory is made then break the while loop
        # so the function will return. Failure will result in
        # an exception caught by the try, which will indicate
        # the loop needs to continue.
        try:
            os.mkdir(outdirectory)
            break
        except OSError:
            pass

        # if limit is an integer, then we need to subtract one
        # then we need to check if limit is now 0. If so,
        # we need to raise an exception indicating failure.
        if not limit is True:
            limit -= 1
            if limit <= 0:
                raise LimitError("Postfix limit was reached before directory could be created.")

        # generate the next postfix based on the iteration
        postfix = generate_postfix(iteration, sequential_postfix)

    return uniqueid, outdirectory


def validate_path(path, allow_whitespace=False,
                  invalid_chars=[":", "/", "\\", "*", "?", ".", "%", "$"]):
    """Validate a user-given path to ensure it does not have any
    restricted characters that could be used for malicious intent,
    or for non-malicious intent that might result in undesired
    operation."""
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
    """Takes an input directory path and an output zip path
    and zips the contents of the directory into a zipfile at
    output path location. The name of the output zipfile
    should be included in the zip_path argument."""
    import os
    import zipfile
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for f in files:
                rel_dir = os.path.relpath(root, directory_path)
                # first arg is file to zip (root/f), and the
                # second arg is the archive name (rel_dir/f)
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
    """A context manager for creating a temporary directory
    that will automatically be removed when it is no longer
    in context."""
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


def get_queryset_arguments(object):
    """This function is used by some of the view functions to
    determine what URL arguments are to be used to filter instance
    queries. For example, finding all layers from a geodatabase in
    a specific AOI, the goedatabase and AOI ids would be used as
    the filters."""
    query_dict = {}
    for kwarg in object.kwargs:
        if kwarg.startswith(URL_FILTER_QUERY_ARG_PREFIX):
            query_lookup = kwarg.replace(
                URL_FILTER_QUERY_ARG_PREFIX,
                '',
                1
            )
            query_value = object.kwargs.get(kwarg)
            query_dict[query_lookup] = query_value
    return query_dict
