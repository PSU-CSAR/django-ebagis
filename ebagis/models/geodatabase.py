from __future__ import absolute_import

from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone
from django.db import transaction

from rest_framework.reverse import reverse

from arcpy_extensions.geodatabase import Geodatabase as arcpyGeodatabase
#from arcpy_extensions.layer import Layer as arcpyLayer

from .. import constants

from .mixins import ProxyMixin
from .directory import Directory
from .file import Raster, Vector, Table


def import_rasters(geodatabase, geodatabase_obj, user, filter=None):
    for raster in geodatabase.rasters:
        if filter is None or raster.name in filter:
            Raster.create(raster, geodatabase_obj, user)


def import_vectors(geodatabase, geodatabase_obj, user, filter=None):
    for vector in geodatabase.featureclasses:
        if filter is None or vector.name in filter:
            Vector.create(vector, geodatabase_obj, user)


def import_tables(geodatabase, geodatabase_obj, user, filter=None):
    for table in geodatabase.tables:
        if filter is None or table.name in filter:
            Table.create(table, geodatabase_obj, user)


class Geodatabase(ProxyMixin, Directory):
    rasters = GenericRelation(Raster, for_concrete_model=False)
    vectors = GenericRelation(Vector, for_concrete_model=False)
    tables = GenericRelation(Table, for_concrete_model=False)

    @property
    def subdirectory_of(self):
        return self.aoi.path

    @classmethod
    @transaction.atomic
    def create(cls, geodatabase_path, user, aoi, id=None):
        gdb_obj = super(Geodatabase, cls).create(aoi, id=id)

        # get all geodatabase layers
        gdb = arcpyGeodatabase.Open(geodatabase_path)

        # copy rasters and create raster and raster data objects
        import_rasters(gdb, gdb_obj, user)

        # copy vectors and create vector and vetor data objects
        import_vectors(gdb, gdb_obj, user)

        # copy tables and create table and table data objects
        import_tables(gdb, gdb_obj, user)

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

    def get_url(self, request):
        kwargs = {}
        objtype = type(self).__name__.lower()
        view_name = "aoi-" + objtype

        if objtype in constants.MULTIPLE_GDBS:
            kwargs["pk"] = self.id
            kwargs["aoi_pk"] = self.aoi_id
        else:
            kwargs["pk"] = self.aoi_id

        return reverse(view_name,
                       kwargs=kwargs,
                       request=request)


class Geodatabase_IndividualArchive(Geodatabase):
    _singular = True

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
    _singular = True

    def __init__(self, *args, **kwargs):
        # override default NO_ARCHIVING with READ_ONLY rule
        self._meta.get_field('archiving_rule').default = \
            constants.READ_ONLY
        super(Geodatabase_ReadOnly, self).__init__(*args, **kwargs)

    class Meta:
        proxy = True


class Surfaces(Geodatabase_ReadOnly):
    class Meta:
        proxy = True

    @property
    def _parent_object(self):
        return self.aoi

class Layers(Geodatabase_IndividualArchive):
    class Meta:
        proxy = True

    @property
    def _parent_object(self):
        return self.aoi


class AOIdb(Geodatabase_ReadOnly):
    _path_name = "aoi"

    class Meta:
        proxy = True

    @property
    def _parent_object(self):
        return self.aoi


class Prism(Geodatabase_GroupArchive):
    @property
    def subdirectory_of(self):
        return self.aoi.prism.path

    @property
    def _parent_object(self):
        return self.prismdir

    def get_url(self, request):
        return super(Prism, self).get_url(request, no_model_name=True)

    class Meta:
        proxy = True


class Analysis(Geodatabase_IndividualArchive):
    class Meta:
        proxy = True

    @property
    def _parent_object(self):
        return self.aoi


class HRUZonesGDB(Geodatabase_ReadOnly):
    @property
    def subdirectory_of(self):
        return self.hru_hruGDB.path

    @property
    def _parent_object(self):
        return self.hru_hruGDB

    @classmethod
    @transaction.atomic
    def create(cls, geodatabase_path, user, aoi, hruzonedata, id=None):
        """
        """
        # specifically calling super on geodatabase as need to get to
        # create method on directory class, not the create method
        # on the geodatabase class, from which HRUZonesGDB inherits
        # because we want to do something different than other gdbs
        # also, need to not save on create as subdirectory_of won't work
        gdb_obj = super(Geodatabase, cls).create(
            aoi,
            name=hruzonedata.name,
            save=False,
            id=id
        )

        # this has a one-to-one relation with its containing model
        # that has not been created yet, so we need to "force" the
        # relation on this end to make the subdirectory_of property
        # actually be calculable and allow saving HRUZonesGDB instance
        gdb_obj.hru_hruGDB = hruzonedata
        gdb_obj.save()

        # get all geodatabase layers
        gdb = arcpyGeodatabase.Open(geodatabase_path)

        # copy required rasters and create raster and raster data objects
        import_rasters(
            gdb,
            gdb_obj,
            user,
            filter=constants.HRU_GDB_LAYERS_TO_SAVE[constants.RASTER_TYPECODE]
        )

        # copy vectors and create vector and vetor data objects
        import_vectors(
            gdb,
            gdb_obj,
            user,
            filter=constants.HRU_GDB_LAYERS_TO_SAVE[constants.FC_TYPECODE]
        )

        # no tables required from HRU GDB

        return gdb_obj

    class Meta:
        proxy = True


class ParamGDB(Geodatabase_ReadOnly):
    _path_name = constants.HRU_PARAM_GDB_NAME

    @property
    def subdirectory_of(self):
        return self.hru_paramGDB.path

    @property
    def _parent_object(self):
        return self.hru_paramGDB

    @classmethod
    @transaction.atomic
    def create(cls, geodatabase_path, user, aoi, hruzonedata, id=None):
        # specifically calling super on geodatabase as need to get to
        # create method on directory class, not the create method
        # on the goedatabase class, from which ParamGDB inherits
        # also, need to not save on create as subdirectory_of won't work
        gdb_obj = super(Geodatabase, cls).create(
            aoi,
            save=False,
            id=id
        )

        # this has a one-to-one relation with its containing model
        # that has not been created yet, so we need to "force" the
        # relation on this end to make the subdirectory_of property
        # actually be calculable and allow saving ParamGDB instance
        gdb_obj.hru_paramGDB = hruzonedata
        gdb_obj.save()

        # get all geodatabase layers
        gdb = arcpyGeodatabase.Open(geodatabase_path)

        # should only need the tables as nothing else should be in gdb
        # copy tables and create table and table data objects
        import_tables(gdb, gdb_obj, user)

        return gdb_obj

    class Meta:
        proxy = True

