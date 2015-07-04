from __future__ import absolute_import

from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone
from django.db import transaction

from arcpy_extensions.geodatabase import Geodatabase as arcpyGeodatabase
#from arcpy_extensions.layer import Layer as arcpyLayer

from ebagis import constants

from .mixins import ProxyMixin
from .directory import Directory
from .file import Raster, Vector, Table


class Geodatabase(ProxyMixin, Directory):
    rasters = GenericRelation(Raster, for_concrete_model=False)
    vectors = GenericRelation(Vector, for_concrete_model=False)
    tables = GenericRelation(Table, for_concrete_model=False)

    @property
    def subdirectory_of(self):
        return self.aoi.path

    @classmethod
    @transaction.atomic
    def create(cls, geodatabase_path, user, aoi):
        gdb_obj = super(Geodatabase, cls).create(aoi)

        # get all geodatabase layers and copy to outdirectory
        gdb = arcpyGeodatabase.Open(geodatabase_path)

        # copy rasters and create raster and raster data objects
        for raster in gdb.rasters:
            Raster.create(raster, gdb_obj, user)

        # copy vectors and create vector and vetor data objects
        for vector in gdb.featureclasses:
            Vector.create(vector, gdb_obj, user)

        # copy tables and create table and table data objects
        for table in gdb.tables:
            Table.create(table, gdb_obj, user)

        return gdb_obj

    def export(self, output_dir, querydate=timezone.now()):
        super(Geodatabase, self).export(output_dir, querydate)
        from arcpy.management import CreateFileGDB
        result = CreateFileGDB(output_dir, self.name)
        outpath = result.getOutput(0)
        for raster in self.rasters.all():
            raster.export(outpath, querydate=querydate)
        for vector in self.vectors.all():
            vector.export(outpath, querydate=querydate)
        for table in self.tables.all():
            table.export(outpath, querydate=querydate)
        return outpath


class Geodatabase_IndividualArchive(Geodatabase):
    def __init__(self, *args, **kwargs):
        # override the default NO_ARCHIVING rule from the
        # directory class with INDIVIDUAL_ARCHIVING rule
        self._meta.get_field('archiving_rule').default = \
            constants.INDIVIDUAL_ARCHIVING
        super(Geodatabase_IndividualArchive, self).__init__(*args, **kwargs)

    class Meta:
        proxy = True


class Geodatabase_GroupArchive(Geodatabase):
    def __init__(self, *args, **kwargs):
        # override default NO_ARCHIVING with GROUP_ARCHIVING rule
        self._meta.get_field('archiving_rule').default = \
            constants.GROUP_ARCHIVING
        super(Geodatabase_GroupArchive, self).__init__(*args, **kwargs)

    class Meta:
        proxy = True


class Geodatabase_ReadOnly(Geodatabase):
    def __init__(self, *args, **kwargs):
        # override default NO_ARCHIVING with READ_ONLY rule
        self._meta.get_field('archiving_rule').default = constants.READ_ONLY
        super(Geodatabase_ReadOnly, self).__init__(*args, **kwargs)

    class Meta:
        proxy = True


class Surfaces(Geodatabase_ReadOnly):
    class Meta:
        proxy = True


class Layers(Geodatabase_IndividualArchive):
    class Meta:
        proxy = True


class AOIdb(Geodatabase_ReadOnly):
    class Meta:
        proxy = True


class Prism(Geodatabase_GroupArchive):
    @property
    def subdirectory_of(self):
        return self.aoi.prism.path

    class Meta:
        proxy = True


class Analysis(Geodatabase_IndividualArchive):
    class Meta:
        proxy = True


class HRUZonesGDB(Geodatabase):
    class Meta:
        proxy = True
