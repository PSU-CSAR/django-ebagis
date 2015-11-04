from __future__ import absolute_import
import os
import shutil
from logging import exception

from django.utils import timezone
from django.contrib.gis.db import models
from django.db import transaction

from rest_framework.reverse import reverse

from .. import constants

from ..settings import AOI_DIRECTORY, GEO_WKID

from ..exceptions import AOIError

from ..utils.validation import validate_aoi
from ..utils.misc import make_short_name
from ..utils import gis

from .base import ABC
from .mixins import CreatedByMixin, DirectoryMixin
from .geodatabase import Surfaces, Layers, AOIdb, Analysis
from .directory import PrismDir, Maps
from .zones import Zones


class AOIManager(models.GeoManager):
    def get_queryset(self):
        return super(AOIManager, self).get_queryset().select_related()


class AOI(CreatedByMixin, DirectoryMixin, ABC):
    shortname = models.CharField(max_length=25)
    boundary = models.MultiPolygonField(srid=GEO_WKID)
    objects = AOIManager()

    # allow recursive parent-child relations
    # db_constraint as false means an AOI with the given ID
    # does not actually need to exist yet; useful if parent and
    # child AOIs are processed out of order
    parent_aoi = models.ForeignKey("self", null=True, blank=True,
                                   related_name="child_aois",
                                   db_constraint=False)

    # data
    surfaces = models.OneToOneField(Surfaces, related_name="aoi_surfaces",
                                    null=True, blank=True)
    layers = models.OneToOneField(Layers, related_name="aoi_layers",
                                  null=True, blank=True)
    aoidb = models.OneToOneField(AOIdb, related_name="aoi_aoidb",
                                 null=True, blank=True)
    _prism = models.OneToOneField(PrismDir, related_name="aoi_prism",
                                  null=True, blank=True)
    analysis = models.OneToOneField(Analysis, related_name="aoi_analysis",
                                    null=True, blank=True)
    _maps = models.OneToOneField(Maps, related_name="aoi_maps",
                                 null=True, blank=True)
    _zones = models.OneToOneField(Zones, related_name="aoi_zones",
                                  null=True, blank=True)

    # for making file system changes
    subdirectory_of = AOI_DIRECTORY

    class Meta:
        unique_together = ("name",)

    @property
    def _parent_object(self):
        return None

    @property
    def prism(self):
        return self._prism.versions.all()

    @property
    def maps(self):
        return self._maps.maps

    @property
    def zones(self):
        return self._zones.hruzones

    @classmethod
    def create_from_upload(cls, upload, temp_aoi_path):
        aoi_name = os.path.splitext(upload.filename)[0]
        aoi_shortname = make_short_name(aoi_name)
        user = upload.user
        comment = upload.comment
        id = upload.object_id
        parent_id = upload.parent_object_id

        return cls.create(aoi_name,
                          aoi_shortname,
                          user,
                          temp_aoi_path,
                          comment=comment,
                          id=id,
                          parent_aoi_id=parent_id)

    @classmethod
    @transaction.atomic
    def create(cls, aoi_name, aoi_shortname, user,
               temp_aoi_path, comment="", id=None, parent_aoi_id=None):
        # validate AOI to import
        aoi_errors = validate_aoi(temp_aoi_path)

        if aoi_errors:
            errormsg = "Errors were encountered with the AOI {}:"\
                .format(temp_aoi_path)
            for error in aoi_errors:
                errormsg += "\n\t{}".format(error)
            raise AOIError(errormsg)

        # get multipolygon WKT from AOI Boundary Layer
        wkt, crs_wkt = gis.get_multipart_wkt_geometry(
            os.path.join(temp_aoi_path, constants.AOI_GDB),
            layername=constants.AOI_BOUNDARY_LAYER
        )

        crs = gis.create_spatial_ref_from_wkt(crs_wkt)

        if gis.get_authority_code_from_spatial_ref(crs) != GEO_WKID:
            dst_crs = gis.create_spatial_ref_from_EPSG(GEO_WKID)
            wkt = gis.reproject_wkt(wkt, crs, dst_crs)

        aoi = cls(name=aoi_name,
                  shortname=aoi_shortname,
                  boundary=wkt,
                  created_by=user,
                  comment=comment,
                  id=id,
                  parent_aoi_id=parent_aoi_id)
        try:
            aoi.save()

            # TODO: convert GDB imports to use celery group or multiprocessing
            # import aoi.gdb
            aoi.aoidb = AOIdb.create(
                os.path.join(temp_aoi_path,
                             constants.AOI_GDB),
                user,
                aoi,
            )

            aoi.save()

            # import surfaces.gdb
            aoi.surfaces = Surfaces.create(
                os.path.join(temp_aoi_path,
                             constants.SURFACES_GDB),
                user,
                aoi,
            )
            aoi.save()

            # import layers.gdb
            aoi.layers = Layers.create(
                os.path.join(temp_aoi_path,
                             constants.LAYERS_GDB),
                user,
                aoi,
            )
            aoi.save()

            # import HRU Zones
            aoi._zones = Zones.create(
                os.path.join(temp_aoi_path,
                             constants.ZONES_DIR_NAME),
                user,
                aoi,
            )
            aoi.save()

            # import analysis.gdb
            aoi.analysis = Analysis.create(
                os.path.join(temp_aoi_path,
                             constants.ANALYSIS_GDB),
                user,
                aoi,
            )
            aoi.save()

            # import prism.gdb -- need to add dir first, then add prism to it
            aoi._prism = PrismDir.create(
                aoi,
                user,
            )
            aoi.save()
            aoi._prism.add_prism(
                os.path.join(temp_aoi_path,
                             constants.PRISM_GDB),
                user,
                aoi,
            )

            # import param.gdb

            # import loose files in param/

            # import param/paramdata.gdb

            # import map docs in maps directory
            aoi._maps = Maps.create(aoi=aoi,
                                    user=user,
                                    name=constants.MAPS_DIR_NAME)
            aoi.save()

        except:
            try:
                if aoi.path:
                    shutil.rmtree(aoi.path)
            except:
                exception("Failed to remove AOI directory on import error.")
            raise

        return aoi

    @transaction.atomic
    def update(self):
        raise NotImplementedError

    def export(self, output_dir, querydate=timezone.now(), outname=None):
        super(AOI, self).export(output_dir, querydate)

        # if no outname provided, use the AOI name
        # as the name of the output AOI directory
        if not outname:
            outname = self.name

        # make the AOI directory in the specified loaction
        outpath = os.path.join(output_dir, outname)
        os.mkdir(outpath)

        # make the metadata file for versioning
        # TODO

        # export each part of the AOI
        self.surfaces.export(outpath, querydate=querydate)
        self.layers.export(outpath, querydate=querydate)
        self.aoidb.export(outpath, querydate=querydate)
        self._prism.export(outpath, querydate=querydate)
        self.analysis.export(outpath, querydate=querydate)
        self._maps.export(outpath, querydate=querydate)
        self._zones.export(outpath, querydate=querydate)

        return outpath

    def get_url(self, request):
        view = self._classname + "-base:detail"
        kwargs = {"pk": str(self.pk)}
        return reverse(view, kwargs=kwargs, request=request)
