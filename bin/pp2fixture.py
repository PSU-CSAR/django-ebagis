from __future__ import print_function, absolute_import

import os
import sys
import argparse
import json

from osgeo import ogr, osr

from ebagis.utils import gis


PP_MODEL = "ebagis_data.pourpoint"

# use more files to keep size down and github happy
NUMBER_OF_FILES = 5


def filepath(path):
    if not os.path.isfile(path):
        argparse.ArgumentTypeError("Path is not a file: {}".format(path))
    return path


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description='Convert pourpoints from a shp '
                    'file into a django fixture file',
    )

    parser.add_argument(
        'pp_shp',
        type=filepath,
        help='Path to a shapefile that contains pourpoints',
    )
    parser.add_argument(
        '-b',
        '--boundary',
        type=filepath,
        help='Path to a shapefile that contains pourpoint boundaries',
        dest='boundary_shp',
    )
    parser.add_argument(
        '-o',
        '--output',
        help='Output fixture file. Default is to output '
             '.json file of same path/name as input shp.',
        dest='output_file',
        default=None,
    )

    # parse the argvs pass in into args
    args = parser.parse_args(argv)

    return vars(args)


def transform_geometry(geom, dst_crs):
    tf = osr.CoordinateTransformation(
        geom.GetSpatialReference(),
        dst_crs,
    )
    geom.Transform(tf)
    return geom


class PourPoint(object):
    def __init__(self, name, point_wkt, awdb_id,
                 boundary_wkt=None, EPSG='4326'):
        self.model = PP_MODEL
        self.name = name
        self.awdb_id = awdb_id
        self.source = 1
        self._EPSG = EPSG
        self.boundary = boundary_wkt
        self.location = "SRID={};{}".format(self._EPSG, point_wkt)

    @classmethod
    def from_feature(cls, feature, dst_crs=None):
        geom = feature.GetGeometryRef()

        if dst_crs:
            geom = transform_geometry(geom, dst_crs)
            EPSG = dst_crs.GetAttrValue("AUTHORITY", 1)
        else:
            EPSG = geom.GetSpatialReference().GetAttrValue("AUTHORITY", 1)

        # we're only storing the 2D coords for points
        geom.FlattenTo2D()

        return cls(
            feature.GetField('name'),
            geom.ExportToWkt(),
            feature.GetField('stationtri'),
            EPSG=EPSG,
        )

    def set_boundary_from_feature(self, feature, dst_crs=None):
        geom = feature.GetGeometryRef()

        if geom.GetGeometryType() == ogr.wkbPolygon:
            # we store all polygons as multipolygons to accomodate
            # AOIs with more complex geometry
            geom = ogr.ForceToMultiPolygon(geom)

        if dst_crs:
            geom = transform_geometry(geom, dst_crs)
            self.EPSG = dst_crs.GetAttrValue("AUTHORITY", 1)
        else:
            self.EPSG = geom.GetSpatialReference().GetAttrValue("AUTHORITY", 1)

        self.boundary = "SRID={};{}".format(
            self._EPSG,
            geom.ExportToWkt(),
        )

    def to_dict(self):
        return {
            "model": self.model,
            "fields": {
                "name": self.name,
                "location": self.location,
                "boundary": self.boundary,
                "awdb_id": self.awdb_id,
                "source": self.source,
            },
        }


def main(pp_shp, output_file, boundary_shp=None):
    if not output_file:
        output_file = os.path.splitext(pp_shp)[0] + '.json'

    dst_crs = gis.create_spatial_ref_from_EPSG(4326)

    ds = ogr.Open(pp_shp)
    layer = ds.GetLayer(0)

    pourpoints = {}

    for feature in layer:
        pp = PourPoint.from_feature(feature, dst_crs)
        pourpoints[pp.awdb_id] = pp

    if boundary_shp:
        ds = ogr.Open(boundary_shp)
        layer = ds.GetLayer(0)

        for feature in layer:
            awdb_id = feature.GetField('stationtri')
            try:
                pourpoints[awdb_id].set_boundary_from_feature(feature, dst_crs)
            except KeyError:
                print("skipped boundary awdb_id {}, name {}".format(
                    awdb_id,
                    feature.GetField('station_nm'),
                ))

    # make list of pp objects
    pp_list = [pp.to_dict() for pp in pourpoints.values()]
    # split list into groups to be written to files
    lists = [pp_list[i::NUMBER_OF_FILES] for i in xrange(NUMBER_OF_FILES)]

    # write sublists to files
    for i, pps in enumerate(lists):
        name, ext = os.path.splitext(output_file)
        output = "{}_{}{}".format(name, i+1, ext)
        with open(output, 'w') as f:
            json.dump(
                pps,
                f,
                sort_keys=True,
                indent=4,
                separators=(',', ': '),
            )


if __name__ == '__main__':
    main(**parse_args(sys.argv[1:]))
