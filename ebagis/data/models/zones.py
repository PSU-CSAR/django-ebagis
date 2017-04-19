from __future__ import absolute_import
import os

from django.utils import timezone

from ebagis import constants

from .directory import Directory
from .geodatabase import HRUZonesGDB, ParamGDB
from .file import File


class HRUZonesData(Directory):
    _CREATE_DIRECTORY_ON_EXPORT = False

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        # override default NO_ARCHIVING with GROUP_ARCHIVING rule
        # that is, everything in the HRUZonesData directory will be
        # versioned if one file changes
        self._meta.get_field('archiving_rule').default = \
            constants.GROUP_ARCHIVING
        super(HRUZonesData, self).__init__(*args, **kwargs)

    @property
    def xml(self):
        return self.files.get(name=constants.HRU_LOG_FILE)

    @property
    def hru(self):
        return self.subdirectories.get(classname=HRUZonesGDB.__name__)

    @property
    def param(self):
        return self.subdirectories.get(classname=ParamGDB.__name__)

    def get_url(self, request):
        return super(HRUZonesData, self).get_url(request, no_model_name=True)

    def import_content(self, directory_to_import):
        # import the .gdb for this HRUZonesData instance
        # check first for hru gdb with _ prefixed: this is pre-cleaned
        # and does not have ignored layers
        hruzones_gdb_name = self.name + constants.GDB_EXT
        hru_gdb_path = os.path.join(directory_to_import, hruzones_gdb_name)
        hru_gdb_path_underscore = os.path.join(directory_to_import,
                                               "_" + hruzones_gdb_name)
        if os.path.exists(hru_gdb_path_underscore):
            hru_gdb_path = hru_gdb_path_underscore

        HRUZonesGDB.create(hru_gdb_path, self, self.created_by, name=self.name)

        # now import the param.gdb for this HRUZonesData instance
        param_gdb_path = os.path.join(
            directory_to_import,
            constants.HRU_PARAM_GDB_NAME + constants.GDB_EXT,
        )

        if os.path.exists(param_gdb_path):
            ParamGDB.create(param_gdb_path, self, self.created_by)

        # lastly import the HRU's xml log file
        hru_XML_path = os.path.join(
            directory_to_import, constants.HRU_LOG_FILE
        )
        File.create(hru_XML_path, self, self.created_by)

    def export_content(self, output_dir, querydate=timezone.now()):
        self.xml.export(output_dir, querydate)
        self.hru.export(output_dir, querydate)
        try:
            self.param.export(output_dir, querydate)
        except AttributeError:
            pass


class HRUZones(Directory):
    _plural_name = "zones"

    class Meta:
        proxy = True

    @property
    def parent_object(self):
        return self.aoi

    @property
    def versions(self):
        return self.subdirectories.filter(classname=HRUZonesData.__name__)

    def import_content(self, directory_to_import):
        HRUZonesData.create(
            directory_to_import,
            self,
            self.created_by,
            name=self.name,
        )

    def export_content(self, output_dir, querydate=timezone.now()):
        versions = self.versions.filter(created_at__lt=querydate)
        versions.latest("created_at").export(output_dir,
                                             querydate=querydate)


class Zones(Directory):
    class Meta:
        proxy = True

    @property
    def hruzones(self):
        return self.subdirectories.filter(classname=HRUZones.__name__)

    def import_content(self, directory_to_import):
        if os.path.exists(directory_to_import):
            hruzones = [d for d in os.listdir(directory_to_import)
                        if os.path.isdir(os.path.join(directory_to_import, d))]

            for hruzone_name in hruzones:
                HRUZones.create(
                    os.path.join(directory_to_import, hruzone_name),
                    self,
                    self.created_by,
                    name=hruzone_name,
                )

    def export_content(self, output_dir, querydate=timezone.now()):
        for hruzone in self.hruzones:
            hruzone.export(output_dir, querydate)
