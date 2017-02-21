from __future__ import absolute_import

from django.contrib.gis.db import models
from django.contrib.gis.measure import D

from arcpy import Geometry, SpatialReference, FromWKT

from ..settings import GEO_WKID, AWDB_QUERY_URL, AWDB_SEARCH_BUFFER

from ..utils.webservices import query_AWDB, gen_query_params_from_point

from .mixins import NameMixin


class PourPoint(NameMixin):
    location = models.PointField(srid=GEO_WKID)
    awdb_id = models.CharField(max_length=30, null=True, blank=True)

    @classmethod
    def match(cls, point, aoi_name=None, awdb_id=None, sr=GEO_WKID):
        # first we try to match to existing points in the table
        existing_point = cls.objects.filter(
            location__distance_lte=(point, D(ft=100))
        ).distance(point).order_by('distance')[0]

        # if we find one we are done
        if existing_point:
            return existing_point

        # if we didn't find one we want to look at the AWDB USGS
        # stations; maybe it's a new station we don't yet have
        # but first let's turn the point into an Arc geometry obejct,
        # so we can work with it and/or reproject if needed
        pointgeom = FromWKT(point, SpatialReference(sr))

        # now we get any matches from the AWDB USGS stations
        awdb_pourpoints = query_AWDB(
            AWDB_QUERY_URL,
            gen_query_params_from_point(point, sr, dist=AWDB_SEARCH_BUFFER)
        )

        # we will take just the closes point, if any
        if awdb_pourpoints['features']:
            features = []
            awdb_sr = SpatialReference(
                        awdb_pourpoints['spatialReference']['wkid']
                )
            for feature in awdb_pourpoints['features']:
                geom = Geometry(
                    [feature['geometry']['x'], feature['geometry']['x']],
                    awdb_sr
                )
                features.append((geom, feature['attributes']))

            closest = features.pop()
            if len(features) >= 1:
                pointgeom = pointgeom.projectAs(awdb_sr)
                distance = pointgeom.distanceTo(closest[0])

                for feature in features:
                    currdist = pointgeom.distanceTo(feature[0])
                    if currdist < distance:
                        distance = currdist
                        closest = feature

            # yay, we found a match, so we are going to
            # create a pourpoint record from the feature
            wkt = closest.projectAs(SpatialReference(GEO_WKID)).WKT
            name = closest[1]['name']
            awdb_id = closest[1]['stationtriplet']

        else:
            # if still haven't found a match, then we just take the AOI's
            # pourpoint and we add it with the name of the AOI
            wkt = pointgeom.projectAs(SpatialReference(GEO_WKID)).WKT
            name = aoi_name

        # we create the actual pourpoint record using the values
        # set in one of the two cases above and and return it
        pourpoint = cls(
            location=wkt,
            name=name,
            awdb_id=awdb_id,
        )
        pourpoint.save()
        return pourpoint
