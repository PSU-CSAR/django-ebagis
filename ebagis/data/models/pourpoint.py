from __future__ import absolute_import

from django.conf import settings

from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance as DistanceTo
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon

from arcpy import Geometry, SpatialReference, FromWKT

from ebagis.utils.webservices import query_AWDB, gen_query_params_from_point
from ebagis.utils.gis import Distance

from ebagis.models.mixins import NameMixin


SIMPLIFY_TOLERANCE = 0.002  # degrees, as features are stored as geography


class PourPoint(NameMixin):
    SOURCE_REFERENCE = 1
    SOURCE_AWDB = 2
    SOURCE_AOI = 3
    SOURCE_CHOICES = (
        (SOURCE_REFERENCE, 'Reference Point'),
        (SOURCE_AWDB, 'AWDB Point'),
        (SOURCE_AOI, 'Imported AOI Point'),
    )

    location = models.PointField(geography=True, srid=settings.GEO_WKID)
    boundary = models.MultiPolygonField(null=True,
                                        geography=True,
                                        srid=settings.GEO_WKID)
    boundary_simple = models.MultiPolygonField(null=True,
                                               geography=True,
                                               srid=settings.GEO_WKID)
    awdb_id = models.CharField(max_length=30, null=True, blank=True)
    source = models.PositiveSmallIntegerField(choices=SOURCE_CHOICES)

    def update_boundary_simple(self,
                               tolerance=SIMPLIFY_TOLERANCE,
                               save=True):
        """Regenerate the boundary_simple from the full-resolution
        boundary. This should only be needed if the full-res boundary is
        updated for some reason. If the boundary_simple is not set it will
        be generated automatically on save, so calling this explicitly
        is not necessary when setting the boundary."""
        if not self.boundary:
            return

        simple_bound = self.boundary.simplify(
            tolerance=tolerance,
            preserve_topology=True,
        )

        # coerce to multipolygon if needed
        if type(simple_bound) != MultiPolygon:
            simple_bound = MultiPolygon(simple_bound)

        self.boundary_simple = simple_bound

        if save:
            self.save()

    def save(self, *args, **kwargs):
        """Override save to generate simplified boundary from
        a full-resolution boundary if the former is set and the
        latter is not."""
        if self.boundary and not self.boundary_simple:
            self.update_boundary_simple(save=False)
        return super(PourPoint, self).save(*args, **kwargs)

    @staticmethod
    def _add_boundary_if_null(pourpoint, aoi_boundary):
        if pourpoint.boundary is None:
            pourpoint.boundary = aoi_boundary
            pourpoint.save()
        return pourpoint

    @classmethod
    def match(cls, point, aoi_boundary,
              aoi_name=None, awdb_id=None, sr=settings.GEO_WKID):
        # first we try to match to existing points in the table
        pnt = GEOSGeometry(point, srid=sr)
        existing_points = cls.objects.filter(
            location__distance_lte=(pnt, Distance(settings.AWDB_SEARCH_BUFFER))
        )

        # if we find only one we can just take it
        if len(existing_points) == 1:
            return cls._add_boundary_if_null(existing_points[0], aoi_boundary)

        # if we find more than one we want just the closest one
        elif len(existing_points) > 1:
            return cls._add_boundary_if_null(
                existing_points.annotate(
                    distance=DistanceTo(
                        'location', pnt)
                    ).order_by('distance')[0],
                aoi_boundary,
            )

        # if we didn't find one we want to look at the AWDB USGS
        # stations; maybe it's a new station we don't yet have
        # but first let's turn the point into an Arc geometry obejct,
        # so we can work with it and/or reproject if needed
        pointgeom = FromWKT(point, SpatialReference(sr))

        # now we get any matches from the AWDB USGS stations
        awdb_pourpoints = query_AWDB(
            settings.AWDB_QUERY_URL,
            gen_query_params_from_point(point,
                                        sr,
                                        dist=settings.AWDB_SEARCH_BUFFER)
        )
        pp_source = cls.SOURCE_AWDB

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
            wkt = closest.projectAs(SpatialReference(settings.GEO_WKID)).WKT
            name = closest[1]['name']
            awdb_id = closest[1]['stationtriplet']

        else:
            # if still haven't found a match, then we just take the AOI's
            # pourpoint and we add it with the name of the AOI
            wkt = pointgeom.projectAs(SpatialReference(settings.GEO_WKID)).WKT
            name = aoi_name
            pp_source = cls.SOURCE_AOI

        # we create the actual pourpoint record using the values
        # set in one of the two cases above and and return it
        pourpoint = cls(
            location=wkt,
            name=name,
            awdb_id=awdb_id,
            boundary=aoi_boundary,
            source=pp_source
        )
        pourpoint.save()
        return pourpoint
