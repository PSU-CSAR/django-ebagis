from __future__ import absolute_import
import os

from django.utils import timezone
from django.contrib.gis.db import models
from django.conf import settings

from rest_framework.reverse import reverse

from ebagis import constants

from ebagis.exceptions import AOIError

from ebagis.models.mixins import CreatedByMixin, NameMixin

from ebagis.utils.validation import validate_aoi, generate_uuid
from ebagis.utils.misc import make_short_name
from ebagis.utils import gis, transaction

from .base import ABC
from .aoi_directory import AOIDirectory
from .pourpoint import PourPoint
from .mixins import SDDateMixin


class AOI(CreatedByMixin, SDDateMixin, NameMixin, ABC):
    shortname = models.CharField(max_length=25)
    boundary = models.MultiPolygonField(geography=True, srid=settings.GEO_WKID)
    pourpoint = models.ForeignKey(PourPoint,
                                  related_name="_aois",
                                  on_delete=models.PROTECT)

    # allow recursive parent-child relations
    # db_constraint as false means an AOI with the given ID
    # does not actually need to exist yet; useful if parent and
    # child AOIs are processed out of order
    parent_aoi = models.ForeignKey("self", null=True, blank=True,
                                   related_name="child_aois",
                                   db_constraint=False,
                                   on_delete=models.SET_NULL)

    class Meta:
        unique_together = ("name", "_active")

    @property
    def parent_object(self):
        return self.parent_aoi

    @property
    def contents(self):
        # we only want "current" (not removed and/or inactive) records
        return self.directory.current().get(classname='AOIDirectory')

    @property
    def _children(self):
        # we need to get all related records--inactive or otherwise
        return [self.directory.get(classname='AOIDirectory')]

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
            settings.GEO_WKID,
            layername=constants.AOI_BOUNDARY_LAYER
        )

        # get pour point WKT from AOI Pourpoint layer
        pourpoint = gis.get_wkt_geometry_and_reproject(
            os.path.join(temp_aoi_path, constants.AOI_GDB),
            settings.GEO_WKID,
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

    @property
    def _archive_name(self):
        """Override as this is the root of the AOI,
        and its archive name is its own.
        """
        return self.name

    @property
    def aoi_path(self):
        """Override as this is the root of the AOI, which has its own name.
        """
        return self.name

    def export(self, output_dir, querydate=timezone.now(),
               create_heirarchy=True):
        return self.contents.export(output_dir,
                                    querydate=querydate,
                                    create_heirarchy=create_heirarchy)

    def get_url(self, request):
        view = self._classname + "-base:detail"
        kwargs = {"pk": str(self.pk)}
        return reverse(view, kwargs=kwargs, request=request)

    @classmethod
    def validate(cls, data):
        if not data['is_update']:
            name = os.path.splitext(data['filename'])[0]
            cls(name=name).validate_unique()
