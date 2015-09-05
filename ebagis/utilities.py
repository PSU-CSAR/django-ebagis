from contextlib import contextmanager



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


def get_seq_next_val(connection, sequence):
    with connection.cursor() as cursor:
            cursor.execute("SELECT nextval('{}');".format(sequence))
            return cursor.fetchall()[0][0]


