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
    dataset = None

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

