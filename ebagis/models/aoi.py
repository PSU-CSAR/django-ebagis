from __future__ import absolute_import
import os

from django.utils import timezone
from django.contrib.gis.db import models

from rest_framework.reverse import reverse

from .. import constants

from ..settings import GEO_WKID

from ..exceptions import AOIError

from ..utils.validation import validate_aoi, generate_uuid
from ..utils.misc import make_short_name
from ..utils import gis, transaction

from .base import ABC
from .aoi_directory import AOIDirectory
from .mixins import CreatedByMixin, DateMixin, UniqueNameMixin
from .pourpoint import PourPoint


class AOI(CreatedByMixin, DateMixin, UniqueNameMixin, ABC):
    shortname = models.CharField(max_length=25)
    boundary = models.MultiPolygonField(geography=True, srid=GEO_WKID)
    pourpoint = models.ForeignKey(PourPoint,
                                  related_name="aois",
                                  on_delete=models.PROTECT)

    # allow recursive parent-child relations
    # db_constraint as false means an AOI with the given ID
    # does not actually need to exist yet; useful if parent and
    # child AOIs are processed out of order
    parent_aoi = models.ForeignKey("self", null=True, blank=True,
                                   related_name="child_aois",
                                   db_constraint=False,
                                   on_delete=models.PROTECT)

    @property
    def parent_object(self):
        return self.parent_aoi

    @property
    def contents(self):
         return self.directory.get(classname='AOIDirectory')

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
        boundary = gis.get_multipart_wkt_geometry_and_reproject(
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
        closest_pourpoint = PourPoint.match(pourpoint,
                                            boundary,
                                            aoi_name=aoi_name)

        # make the AOI model
        aoi = cls(
            name=aoi_name,
            shortname=aoi_shortname,
            boundary=boundary,
            created_by=user,
            comment=comment,
            id=id,
            parent_aoi_id=parent_aoi_id,
            pourpoint=closest_pourpoint,
        )
        aoi.save()

        # make the AOIDirectory model, which will import
        # all the AOI files to the filesystem
        # we have to generate the UUID before we create
        # the object, as it is required to bootstrap the
        # filesystem operations (it is the directory name)
        AOIDirectory.create(temp_aoi_path, aoi, user,
                            id=generate_uuid(AOIDirectory))

        return aoi

    @transaction.atomic
    def update(self):
        raise NotImplementedError

    def export(self, output_dir, querydate=timezone.now(), outname=None):
        outname = outname if outname else self.shortname
        return self.contents.export(output_dir,
                                    querydate=querydate,
                                    outname=outname)

    def get_url(self, request):
        view = self._classname + "-base:detail"
        kwargs = {"pk": str(self.pk)}
        return reverse(view, kwargs=kwargs, request=request)
