from __future__ import absolute_import, print_function

from math import floor, ceil

from ctypes import c_char_p, c_int, c_void_p, POINTER, c_double

from django.contrib.gis.gdal import GDALRaster
from django.contrib.gis.gdal.libgdal import lgdal
from django.contrib.gis.gdal.prototypes.raster import void_output
from django.contrib.gis.gdal.prototypes.generation import voidptr_output


def px_coords_from_geographic_coords(gdal_raster, pointcoords, roundfn=floor):
    image = gdal_raster

    # get raster edge coords
    left = image.geotransform[0]
    top = image.geotransform[3]
    right = image.width * image.geotransform[1] + image.geotransform[0]
    bottom = image.height * image.geotransform[5] + image.geotransform[3]

    # calc px coords for each set of point coords
    pxcoords = []
    for coords in pointcoords:
        col = int(roundfn(image.width * (coords[0] - left) / (right - left)))
        row = int(roundfn(image.height * (coords[1] - top) / (bottom - top)))
        pxcoords.append((row, col))

    return pxcoords


def geographic_coords_from_px_coords(gdal_raster, pxcoords):
    """
    uses (row, col) format for pxcoords
    """
    image = gdal_raster

    # get raster edge coords
    left = image.geotransform[0]
    top = image.geotransform[3]
    horz_px_size = image.geotransform[1]
    vert_px_size = image.geotransform[5]

    # calc geo coords for each set of px coords
    pointcoords = []
    for coord in pxcoords:
        x = left + coord[1] * horz_px_size
        y = top + coord[0] * vert_px_size
        pointcoords.append((x, y))

    return pointcoords


def check_geom_is_polygon(geom):
    from django.contrib.gis.gdal import OGRGeomType

    if geom.geom_type not in [
        OGRGeomType('POLYGON'),
        OGRGeomType('MULTIPOLYGON')
    ]:
        raise TypeError(
            'Only MultiPolygon and Polygon types supported, not {}'.format(
                type(geom)
            )
        )


def extend_raster(gdal_raster):
    gdal_raster.clip = clip.__get__(gdal_raster)
    gdal_raster.mask = mask.__get__(gdal_raster)
    return gdal_raster


def clip(self, ogr_geom):
    check_geom_is_polygon(ogr_geom)

    # reproject geom to match raster
    transformed_geom = ogr_geom.transform(self.srs, clone=True) \
        if ogr_geom.srs != self.srs else ogr_geom

    # find the raster cells for the clipped origin and antiorigin
    # (the latter is the lower right corner)
    origin_x, antiorigin_y, antiorigin_x, origin_y = transformed_geom.extent
    origin_pxcoords = px_coords_from_geographic_coords(
        self,
        ((origin_x, origin_y),),
    )[0]
    antiorigin_pxcoords = px_coords_from_geographic_coords(
        self,
        ((antiorigin_x, antiorigin_y),),
        roundfn=ceil,
    )[0]

    new_origin = geographic_coords_from_px_coords(self, (origin_pxcoords,))[0]

    height = antiorigin_pxcoords[0] - origin_pxcoords[0]
    width = antiorigin_pxcoords[1] - origin_pxcoords[1]

    raster = extend_raster(self.warp(
        {
            'width': width,
            'height': height,
            'origin': new_origin,
        },
    ))

    return raster


# GDALRasterizeOptionsNew
# papszArgv NULL terminated list of options
#           (potentially including filename and open options too), or NULL.
#           The accepted options are the ones of the gdal_rasterize utility.
# psOptionsForBinary	(output) may be NULL...
rasterize_options = voidptr_output(
    lgdal['GDALRasterizeOptionsNew'],
    [
        POINTER(c_char_p),
        c_char_p,
    ],
)

# GDALRasterize
# pszDest	the destination dataset path or NULL.
# hDstDS	the destination dataset or NULL.
# hSrcDataset	the source dataset handle.
# psOptionsIn	the options struct returned by GDALRasterizeOptionsNew() or NULL.
# pbUsageError	the pointer to int variable to determine
#     any usage error has occurred or NULL.
rasterize = void_output(
    lgdal['GDALRasterize'],
    [
        c_char_p,
        c_void_p,
        c_void_p,
        c_void_p,
        POINTER(c_int),
    ],
)


# GDALRasterizeGeometries
# GDALDatasetH hDS output data, must be opened in update mode.
# int nBandCount the number of bands to be updated.
# int * panBandList the list of bands to be updated.
# int nGeomCount the number of geometries being passed in pahGeometries.
# OGRGeometryH * pahGeometries the array of geometries to burn in.
# OGRGeometryH pfnTransformer transformation to apply to geometries to put into
#     pixel/line coordinates on raster.  If NULL a geotransform based one will
#     be created internally.
# void pTransformArg callback data for transformer.
# double * padfGeomBurnValue the array of values to burn into the raster.
#     There should be nBandCount values for each geometry.
# char ** papszOptions special options controlling rasterization
#
#   - "ALL_TOUCHED": May be set to TRUE to set all pixels touched
#         by the line or polygons, not just those whose center
#         is within the polygon or that are selected by
#         brezenhams line algorithm.  Defaults to FALSE.
#
#   - "BURN_VALUE_FROM": May be set to "Z" to use the Z values of the
#         geometries. dfBurnValue is added to this before burning.
#         Defaults to GDALBurnValueSrc.GBV_UserBurnValue in which
#         case just the dfBurnValue is burned. This is implemented
#         only for points and lines for now. The M value may be
#         supported in the future.
#
#   - "MERGE_ALG": May be REPLACE (the default) or ADD.  REPLACE results in
#         overwriting of value, while ADD adds the new value to the
#         existing raster, suitable for heatmaps for instance.
#
#   - "CHUNKYSIZE": The height in lines of the chunk to operate on.
#         The larger the chunk size the less times we need to make
#         a pass through all the shapes. If it is not set or set to
#         zero the default chunk size will be used. Default size
#         will be estimated based on the GDAL cache buffer size using
#         formula: cache_size_bytes/scanline_size_bytes, so the chunk
#         will not exceed the cache. Not used in OPTIM=RASTER mode.
#
# GDALProgressFunc pfnProgress the progress function to report completion.
# void pProgressArg callback data for progress function.
#
# returns CE_None on success or CE_Failure on error.
rasterize_geometries = void_output(
    lgdal['GDALRasterizeGeometries'],
    [
        c_void_p,
        c_int,
        POINTER(c_int),
        c_int,
        c_void_p,
        c_void_p,
        c_void_p,
        POINTER(c_double),
        POINTER(c_char_p),
        c_void_p,
        c_void_p,
    ],
)


def mask(
    self,
    ogr_geom,
    all_touched=False,
    clone=False,
):
    """
    Clips an instance of django.contrib.gis.gdal.GDALRaster to the shape of
    a django.contrib.gis.geos.OGRGeometry instance.
    """
    check_geom_is_polygon(ogr_geom)

    # reproject geom to match raster
    transformed_geom = ogr_geom.transform(self.srs, clone=True) \
        if ogr_geom.srs != self.srs else ogr_geom

    # create a temp raster dataset for masking
    masked = GDALRaster({
        'srid': self.srid,
        'width': self.width,
        'height': self.height,
        'origin': self.origin,
        'scale': self.scale,
        'skew': self.skew,
        'nr_of_bands': 1,
        'datatype': 5,
    })

    # we only need one band for the mask
    band_arr = (c_int * 1)()
    band_arr[:] = [1]

    # could make the geom arg a list in the future
    # if wanting to provide a means to mask with
    # multiple geometries
    geom_arr = (c_void_p * 1)()
    geom_arr[:] = [transformed_geom.ptr]

    # we're simply using a burn  value of 1 for each band
    burn_arr = (c_double * len(band_arr))()
    burn_arr[:] = [1] * len(band_arr)

    # create the opts to set all touched
    opts = []
    if all_touched:
        opts.append('ALL_TOUCHED')

    # make the opts a C array
    opt_arr = (c_char_p * len(opts))()
    opt_arr[:] = opts

    # call the C function to make the mask
    rasterize_geometries(
        masked.ptr,
        len(band_arr),
        band_arr,
        len(geom_arr),
        geom_arr,
        None,
        None,
        burn_arr,
        opt_arr,
        None,
        None,
    )

    # probably don't need this with the MEM driver,
    # but it shouldn't hurt anything to have it
    masked._flush()

    #masked.warp({'driver': 'GTiff', 'name': 'mask.tif'})

    # make a copy of the raster if we need to clone
    raster = self.warp({}) if clone else self

    # mask each band in the output raster
    mask = masked.bands[0].data()
    mask = mask == 0
    print(mask)
    for band in raster.bands:
        d = band.data()
        d[mask] = band.nodata_value
        print(d)
        band.data(data=d)

    return raster
