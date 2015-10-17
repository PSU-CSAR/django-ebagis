from __future__ import absolute_import
import os

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.utils import timezone
from django.db import transaction

from .. import constants

from .base import ABC
from .mixins import DirectoryMixin, AOIRelationMixin, CreatedByMixin
from .file import MapDocument


class Directory(DirectoryMixin, CreatedByMixin, AOIRelationMixin, ABC):
    _path_name = None

    class Meta:
        abstract = True

    @classmethod
    @transaction.atomic
    def create(cls, aoi, user, name=None, save=True, id=None):
        if not name:
            name = cls._path_name if cls._path_name else cls.__name__.lower()
        dir_obj = cls(aoi=aoi, name=name, id=id, created_by=user)
        if save:
            dir_obj.save()
        return dir_obj

    @transaction.atomic
    def update(self):
        raise NotImplementedError


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
    _singular = True

    @property
    def subdirectory_of(self):
        return self.aoi.path

    @property
    def _parent_object(self):
        return self.aoi

    @classmethod
    @transaction.atomic
    def create(cls, aoi, user, id=None):
        prismdir_obj = super(PrismDir, cls).create(
            aoi,
            name=constants.PRISM_DIR_NAME,
            id=id,
            user=user,
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

