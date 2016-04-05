from __future__ import absolute_import
import os

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.utils import timezone

from ..utils import transaction
from .. import constants

from .base import ABC
from .mixins import DirectoryMixin, AOIRelationMixin, CreatedByMixin
from .file import MapDocument


class DirectoryManager(models.Manager):
    """Model manager class used by the Directory Class"""
    def get_queryset(self):
        return super(DirectoryManager, self).get_queryset(
            ).select_related()#.prefetch_related(*self.model._prefetch)


class Directory(DirectoryMixin, CreatedByMixin, AOIRelationMixin, ABC):
    _prefetch = []
    _path_name = None

    _archive_fields = {"read_only": ["id", "created_at", "created_by"],
                       "writable": ["name", "comment"]}

    class Meta:
        abstract = True

    @classmethod
    @transaction.atomic
    def create(cls, aoi, user, name=None, save=True, id=None, comment=""):
        if not name:
            name = cls._path_name if cls._path_name else cls.__name__.lower()
        dir_obj = cls(aoi=aoi, name=name, id=id,
                      created_by=user, comment=comment)
        if save:
            dir_obj.save()
        return dir_obj

    @transaction.atomic
    def update(self):
        raise NotImplementedError


class Maps(Directory):
    _prefetch = ["maps"]
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
    _prefetch = ["versions"]
    versions = models.ManyToManyField("Prism", related_name="prismdir")
    _singular = True

    @property
    def subdirectory_of(self):
        return self.aoi.path

    @property
    def _parent_object(self):
        return self.aoi

    @classmethod
    @transaction.atomic
    def create(cls, aoi, user, id=None, comment=""):
        prismdir_obj = super(PrismDir, cls).create(
            aoi,
            name=constants.PRISM_DIR_NAME,
            id=id,
            user=user,
            comment=comment,
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
