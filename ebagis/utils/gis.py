from __future__ import absolute_import

from django.contrib.gis.measure import Distance as DjangoDistance


class Distance(DjangoDistance):
    """Override the Django GIS Distance object to allow passing in
    the linear distance as a string, like '100 Feet' or '35M',
    in addition to the default keyword arg behavior like Distance(ft=30)."""
    # we want to grab the lowercase unit aliases from the base class
    # so we can add some pluralized units for ease of use
    LALIAS = DjangoDistance.LALIAS.copy()
    LALIAS.update({
        k+"s": v for k, v in DjangoDistance.ALIAS.iteritems()
        if " " not in k and k.lower() != 'foot'.lower()
    })
    LALIAS['feet'] = LALIAS['foot']

    def __init__(self, distance=None, **kwargs):
        import re
        # if a single arg is passed it is either a unitless distance,
        # or it is a string of the distance and needs to be parsed
        if distance is not None:
            match = re.match(
                r'^(?P<measure>[0-9.]+)\s*(?P<unit>[a-zA-Z]*)$',
                distance,
            )
            if match and match.group('unit'):
                # then we parsed a distance and a unit
                kwargs[match.group('unit')] = match.group('measure')
            elif match:
                # then we did not get a unit, just a measure
                # so we'll just use the standard unit (meter)
                kwargs[self.STANDARD_UNIT] = match.group('measure')
            else:
                # whatever was passed did not fit the expected format
                raise AttributeError(
                    'Unable to parse distance: {}'.format(distance)
                )
        return super(Distance, self).__init__(**kwargs)

    def __getattr__(self, name):
        unit = self.unit_attname(name)
        return self.standard / self.UNITS[unit]


def get_multipart_wkt_geometry_and_reproject(sourcefile,
                                             destEPSG,
                                             layername=None):
        wkt, crs_wkt = get_multipart_wkt_geometry(sourcefile,
                                                  layername=layername)

        crs = create_spatial_ref_from_wkt(crs_wkt)

        if get_authority_code_from_spatial_ref(crs) != destEPSG:
            dst_crs = create_spatial_ref_from_EPSG(destEPSG)
            wkt = reproject_wkt(wkt, crs, dst_crs)

        return wkt


def get_multipart_wkt_geometry(sourcefile, layername=None):
    """extract a single multipolygon geometry from an sourcefile
    containing polygon geometries"""
    geometries, crs_wkt = get_wkt_geometry(sourcefile, layername=layername)
    return (wkt_polygons_to_multipolygon(geometries), crs_wkt)


def get_wkt_geometry_and_reproject(sourcefile, destEPSG, layername=None):
    wkt, src_crs = get_wkt_geometry(sourcefile, layername=layername)
    return reproject_wkt(wkt[0], src_crs, destEPSG)


def get_wkt_geometry(sourcefile, layername=None):
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

    return (geometries, crs_wkt)


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
            raise TypeError("Invalid or unknown geometry type detected.")

        # append the geometry to this list, sans geometry type tag
        cleaned_wkts.append(wkt)

    # join the individual geometeries in the list into a single multipolygon
    return "MULTIPOLYGON (" + ",".join(cleaned_wkts) + ")"


def reproject_wkt(wkt, src_crs, dst_crs):
    from osgeo import ogr, osr

    src_crs = validate_spatial_ref(src_crs)
    dst_crs = validate_spatial_ref(dst_crs)

    tf = osr.CoordinateTransformation(src_crs, dst_crs)
    geom = ogr.CreateGeometryFromWkt(wkt)
    geom.Transform(tf)
    return geom.ExportToWkt()


def get_authority_code_from_spatial_ref(spatial_ref):
    return spatial_ref.GetAttrValue("AUTHORTIY", 1)


def validate_spatial_ref(sr):
    from osgeo import osr
    if not isinstance(sr, osr.SpatialReference):
        try:
            sr = create_spatial_ref_from_EPSG(sr)
        except:
            sr = create_spatial_ref_from_wkt(sr)
    return sr


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


def generate_envelope(point, bufferdist):
    from osgeo import ogr
    x, y, z = ogr.CreateGeometryFromWkt(point).GetPoint()
    return (
        x - bufferdist/2.0,
        y - bufferdist/2.0,
        x + bufferdist/2.0,
        y + bufferdist/2.0,
    )
