from __future__ import absolute_import
import os
import shutil
from logging import exception

from django.utils import timezone
from django.contrib.gis.db import models

from rest_framework.reverse import reverse

from .. import constants

from ..settings import AOI_DIRECTORY, GEO_WKID

from ..exceptions import AOIError

from ..utils.validation import validate_aoi
from ..utils.misc import make_short_name
from ..utils import gis, transaction

from .base import ABC
from .mixins import CreatedByMixin, DirectoryMixin
from .geodatabase import Surfaces, Layers, AOIdb, Analysis
from .directory import PrismDir, Maps
from .zones import Zones
from .pourpoint import PourPoint


class AOI(CreatedByMixin, DirectoryMixin, ABC):
    shortname = models.CharField(max_length=25)
    boundary = models.MultiPolygonField(srid=GEO_WKID)
    pourpoint = models.ForeignKey(PourPoint, related_name="aois")

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

    _archive_fields = {
        "read_only": ["id", "created_at", "created_by", "parent_aoi",
                      "surfaces", "layers", "aoidb", "_prism", "analysis",
                      "_maps", "_zones"],
        "writable": ["name", "comment"]
    }

    # for making file system changes
    subdirectory_of = AOI_DIRECTORY

    class Meta:
        unique_together = ("name",)

    @property
    def _metadata_path(self):
        """again overriding this property to put the metadata file
        inside the AOI directory. While this conflicts with all other
        directory subclasses, I believe the case of the AOI object
        is differnet enough to warrant this change.
        """
        return self._path

    @property
    def _filesystem_name(self):
        """This property is the name of the file system directory
        created when an AOI instance is saved.

        Here we use the ID and not the name so we can do two things:
            1) allow multiple AOIs with the same name (though this is
               currently prevented with a database constraint)
            2) change the name of an existing AOI and not have to change
               anything in the file system (except the metadata file)
        """
        return str(self.id)

    @property
    def _parent_object(self):
        return self.parent_aoi

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
        wkt = gis.get_multipart_wkt_geometry_and_reproject(
            os.path.join(temp_aoi_path, constants.AOI_GDB),
            GEO_WKID,
            layername=constants.AOI_BOUNDARY_LAYER
        )

        # get pour point WKT from AOI Pourpoint layer
        pourpoint = gis.get_wkt_geometry_and_reproject(
            os.path.join(temp_aoi_path, constants.AOI_GDB),
            GEO_WKID,
            layername=constants.AOI_POURPOINT_LAYER
        )

        # find or create pourpoint
        closest_pourpoint = PourPoint.match(pourpoint, aoi_name)

        aoi = cls(
            name=aoi_name,
            shortname=aoi_shortname,
            boundary=wkt,
            created_by=user,
            comment=comment,
            id=id,
            parent_aoi_id=parent_aoi_id,
            pourpoint=closest_pourpoint,
        )

        try:
            aoi.save()

            # TODO: convert GDB imports to use celery group or multiprocessing
            # though how to maintain thread-safety, and manage transactions?

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
            aoi._maps = Maps.create(
                os.path.join(temp_aoi_path,
                             constants.MAPS_DIR),
                user,
                aoi,
            )

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
