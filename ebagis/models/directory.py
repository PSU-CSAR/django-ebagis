from __future__ import absolute_import
import os

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.utils import timezone
from django.db import transaction

from .. import constants

from .mixins import DirectoryMixin, AOIRelationMixin
from .base import RandomPrimaryIdModel
from .file import MapDocument


class Directory(DirectoryMixin, AOIRelationMixin, RandomPrimaryIdModel):
    _path_name = None

    class Meta:
        abstract = True

    @classmethod
    @transaction.atomic
    def create(cls, aoi, name=None):
        if not name:
            name = cls._path_name if cls._path_name else cls.__name__.lower()
        dir_obj = cls(aoi=aoi, name=name)
        dir_obj.save()
        return dir_obj


class Maps(Directory):
    maps = GenericRelation(MapDocument, for_concrete_model=False)

    @property
    def subdirectory_of(self):
        return self.aoi.path

    def export(self, output_dir, querydate=timezone.now()):
        super(Maps, self).export(output_dir, querydate)
        outpath = os.path.join(output_dir, self.name)
        os.mkdir(outpath)
        for mapdoc in self.maps.all():
            mapdoc.export(outpath, querydate=querydate)
        return outpath


class PrismDir(Directory):
    versions = models.ManyToManyField("Prism", related_name="prismdir")

    @property
    def subdirectory_of(self):
        return self.aoi.path

    @classmethod
    @transaction.atomic
    def create(cls, aoi):
        prismdir_obj = super(PrismDir, cls).create(
            aoi, name=constants.PRISM_DIR_NAME
        )

        return prismdir_obj

    def add_prism(self, path, user, aoi):
        from .geodatabase import Prism
        self.versions.add(Prism.create(path, user, aoi))

    def export(self, output_dir, querydate=timezone.now()):
        super(PrismDir, self).export(output_dir, querydate)
        filtered = self.versions.filter(created_at__lt=querydate)
        return filtered.latest("created_at").export(output_dir,
                                                    querydate=querydate)
