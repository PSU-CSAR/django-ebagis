from __future__ import absolute_import

from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone

from arcpy_extensions.geodatabase import Geodatabase as arcpyGeodatabase
#from arcpy_extensions.layer import Layer as arcpyLayer

from .. import constants
from ..utils import transaction

from .mixins import ProxyMixin
from .directory import Directory
from .file import Raster, Vector, Table


def import_rasters(geodatabase, geodatabase_obj, user, filter=None):
    import_layers(geodatabase.rasters, Raster, geodatabase_obj, user, filter)


def import_vectors(geodatabase, geodatabase_obj, user, filter=None):
    import_layers(geodatabase.featureclasses,
                  Vector, geodatabase_obj, user, filter)


def import_tables(geodatabase, geodatabase_obj, user, filter=None):
    import_layers(geodatabase.tables, Table, geodatabase_obj, user, filter)


def import_layers(layers, layer_class, geodatabase_obj, user, filter=None):
    for layer in layers:
        if filter is None or layer.name in filter:
            layer_class.create(layer, geodatabase_obj, user)


class Geodatabase(ProxyMixin, Directory):
    _prefetch = ["rasters", "vectors", "tables"]
    rasters = GenericRelation(Raster, for_concrete_model=False)
    vectors = GenericRelation(Vector, for_concrete_model=False)
    tables = GenericRelation(Table, for_concrete_model=False)

    class Meta:
        index_together = [
            ["id", "classname"],
        ]

    @property
    def subdirectory_of(self):
        return self.aoi.path

    @classmethod
    @transaction.atomic
    def create(cls, geodatabase_path, user, aoi, id=None, comment=""):
        gdb_obj = super(Geodatabase, cls).create(
            aoi,
            id=id,
            user=user,
            comment=comment,
        )

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
    _plural_name = "surfaces"

    class Meta:
        proxy = True

    @property
    def _parent_object(self):
        return self.aoi


class Layers(Geodatabase_IndividualArchive):
    _plural_name = "layers"

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
        return self.aoi._prism.path

    @property
    def _parent_object(self):
        # a many-to-many realtionship used to implement a
        # one-to-many relationship. Need to just get the first
        # of the list returned, as there should only ever be
        # one object in the list, as it is one-to-many.
        return self.aoi

    def get_url(self, request):
        return super(Prism, self).get_url(request, no_s=True)

    class Meta:
        proxy = True


class Analysis(Geodatabase_IndividualArchive):
    _plural_name = "analyses"

    class Meta:
        proxy = True

    @property
    def _parent_object(self):
        return self.aoi


class HRUZonesGDB(Geodatabase_ReadOnly):
    _prefetch = ["rasters", "vectors", "tables", "hru_zones_data"]

    @property
    def subdirectory_of(self):
        return self.hru_zones_data.path

    @property
    def _parent_object(self):
        return self.hru_zones_data

    @classmethod
    @transaction.atomic
    def create(cls, geodatabase_path, user, aoi, hruzonedata,
               id=None, comment=""):
        """
        """
        # specifically calling super on geodatabase as need to get to
        # create method on directory class, not the create method
        # on the geodatabase class from which HRUZonesGDB inherits,
        # because we want to do something different than other gdbs
        # also, need to not save on create as subdirectory_of won't work
        gdb_obj = super(Geodatabase, cls).create(
            aoi,
            name=hruzonedata.name,
            save=False,
            id=id,
            user=user,
            comment=comment,
        )

        # this has a one-to-one relation with its containing model
        # that has not been created yet, so we need to "force" the
        # relation on this end to make the subdirectory_of property
        # actually be calculable and allow saving HRUZonesGDB instance
        #
        # this is a magic value defined on the HRUZonesData class
        # as the related_name for the hruzonesgdb field
        gdb_obj.hru_zones_data = hruzonedata
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
    _prefetch = ["rasters", "vectors", "tables", "hru_zones_data"]
    _path_name = constants.HRU_PARAM_GDB_NAME

    @property
    def subdirectory_of(self):
        return self.hru_zones_params.path

    @property
    def _parent_object(self):
        return self.hru_zones_params

    @classmethod
    @transaction.atomic
    def create(cls, geodatabase_path, user, aoi, hruzoneparams,
               id=None, comment=""):
        # specifically calling super on geodatabase as need to get to
        # create method on directory class, not the create method
        # on the goedatabase class, from which ParamGDB inherits
        # also, need to not save on create as subdirectory_of won't work
        gdb_obj = super(Geodatabase, cls).create(
            aoi,
            save=False,
            id=id,
            user=user,
            comment=comment,
        )

        # this has a one-to-one relation with its containing model
        # that has not been created yet, so we need to "force" the
        # relation on this end to make the subdirectory_of property
        # actually be calculable and allow saving ParamGDB instance
        #
        # this is a magic value defined on the HRUZonesData class
        # as the related_name for the paramgdb field
        gdb_obj.hru_zones_params = hruzoneparams
        gdb_obj.save()

        # get all geodatabase layers
        gdb = arcpyGeodatabase.Open(geodatabase_path)

        # should only need the tables as nothing else should be in gdb
        # copy tables and create table and table data objects
        import_tables(gdb, gdb_obj, user)

        return gdb_obj

    class Meta:
        proxy = True
