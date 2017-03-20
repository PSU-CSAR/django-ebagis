from __future__ import absolute_import

from django.utils import timezone

from arcpy_extensions.geodatabase import Geodatabase as arcpyGeodatabase

from .. import constants

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


class Geodatabase(Directory):
    class Meta:
        proxy = True

    _prefetch = ["rasters", "vectors", "tables"]

    @property
    def rasters(self):
        return self.files.filter(classname=Raster.__name__)

    @property
    def vectors(self):
        return self.files.filter(classname=Vector.__name__)

    @property
    def tables(self):
        return self.files.filter(classname=Table.__name__)

    def import_content(self, geodatabase_to_import):
        # get all geodatabase layers
        gdb = arcpyGeodatabase.Open(geodatabase_to_import)

        # copy rasters and create raster and raster data objects
        import_rasters(gdb, self, self.created_by)

        # copy vectors and create vector and vetor data objects
        import_vectors(gdb, self, self.created_by)

        # copy tables and create table and table data objects
        import_tables(gdb, self, self.created_by)

    def export(self, output_dir, querydate=timezone.now()):
        self._validate_querydate(querydate)
        from arcpy.management import CreateFileGDB
        result = CreateFileGDB(output_dir, self.name)
        outpath = result.getOutput(0)
        for raster in self.rasters:
            raster.export(outpath, querydate=querydate)
        for vector in self.vectors:
            vector.export(outpath, querydate=querydate)
        for table in self.tables:
            table.export(outpath, querydate=querydate)
        return outpath


class Geodatabase_IndividualArchive(Geodatabase):
    class Meta:
        proxy = True

    _singular = True

    def __init__(self, *args, **kwargs):
        # override the default NO_ARCHIVING rule from the
        # directory class with INDIVIDUAL_ARCHIVING rule
        self._meta.get_field('archiving_rule').default = \
            constants.INDIVIDUAL_ARCHIVING
        super(Geodatabase_IndividualArchive, self).__init__(*args, **kwargs)


class Geodatabase_GroupArchive(Geodatabase):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        # override default NO_ARCHIVING with GROUP_ARCHIVING rule
        self._meta.get_field('archiving_rule').default = \
            constants.GROUP_ARCHIVING
        super(Geodatabase_GroupArchive, self).__init__(*args, **kwargs)


class Geodatabase_ReadOnly(Geodatabase):
    class Meta:
        proxy = True

    _singular = True

    def __init__(self, *args, **kwargs):
        # override default NO_ARCHIVING with READ_ONLY rule
        self._meta.get_field('archiving_rule').default = \
            constants.READ_ONLY
        super(Geodatabase_ReadOnly, self).__init__(*args, **kwargs)


class Surfaces(Geodatabase_ReadOnly):
    _plural_name = "surfaces"

    class Meta:
        proxy = True


class Layers(Geodatabase_IndividualArchive):
    _plural_name = "layers"

    class Meta:
        proxy = True


class AOIdb(Geodatabase_ReadOnly):
    _path_name = "aoi"

    class Meta:
        proxy = True


class Prism(Geodatabase_GroupArchive):
    class Meta:
        proxy = True

    @property
    def parent_object(self):
        return self.aoi

    def get_url(self, request):
        return super(Prism, self).get_url(request, no_s=True)


class Analysis(Geodatabase_IndividualArchive):
    _plural_name = "analyses"

    class Meta:
        proxy = True


class HRUZonesGDB(Geodatabase_ReadOnly):
    class Meta:
        proxy = True

    def import_content(self, geodatabase_to_import):
        # get all geodatabase layers
        gdb = arcpyGeodatabase.Open(geodatabase_to_import)

        # copy required rasters and create raster and raster data objects
        import_rasters(
            gdb, self, self.created_by,
            filter=constants.HRU_GDB_LAYERS_TO_SAVE[constants.RASTER_TYPECODE],
        )

        # copy required vectors and create vector and vetor data objects
        import_vectors(
            gdb, self, self.created_by,
            filter=constants.HRU_GDB_LAYERS_TO_SAVE[constants.FC_TYPECODE],
        )

        # no tables required from HRU GDB


class ParamGDB(Geodatabase_ReadOnly):
    _path_name = constants.HRU_PARAM_GDB_NAME

    class Meta:
        proxy = True

    def import_content(self, geodatabase_to_import):
        # get all geodatabase layers
        gdb = arcpyGeodatabase.Open(geodatabase_to_import)

        # should only need the tables as nothing else should be in gdb
        # copy tables and create table and table data objects
        import_tables(gdb, self, self.created_by)
