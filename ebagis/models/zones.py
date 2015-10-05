from __future__ import absolute_import
import os

from django.utils import timezone
from django.contrib.gis.db import models
from django.db import transaction

from .. import constants

from .directory import Directory
from .geodatabase import HRUZonesGDB, ParamGDB
from .file import XML


class HRUZonesData(Directory):
    xml = models.OneToOneField(XML, related_name="hru_xml", null=True)
    hruzonesgdb = models.OneToOneField(HRUZonesGDB,
                                       null=True)
    paramgdb = models.OneToOneField(ParamGDB,
                                    null=True)
    hruzones = models.ForeignKey("HRUZones", related_name="versions")

    def __init__(self, *args, **kwargs):
        # override default NO_ARCHIVING with GROUP_ARCHIVING rule
        # that is, everything in the HRUZonesData directory will be
        # versioned if one file changes
        self._meta.get_field('archiving_rule').default = \
            constants.GROUP_ARCHIVING
        super(HRUZonesData, self).__init__(*args, **kwargs)

    @property
    def subdirectory_of(self):
        return self.hruzones.path

    @property
    def _parent_object(self):
        return self.hruzones

    def get_url(self, request):
        return super(HRUZonesData, self).get_url(request, no_model_name=True)

    @classmethod
    @transaction.atomic
    def create(cls, temp_hru_path, hruzones, user, id=None):
        # create a new HRUZonesData instance and save it
        hruzonesdata_obj = HRUZonesData(aoi=hruzones.aoi,
                                        name=hruzones.name,
                                        hruzones=hruzones,
                                        created_by=user,
                                        id=id)
        hruzonesdata_obj.save()

        # import the .gdb for this HRUZonesData instance
        # check first for hru gdb with _ prefixed: this is pre-cleaned
        # and does not have ignored layers
        hruzones_gdb_name = hruzones.name + constants.GDB_EXT
        hru_gdb_path = os.path.join(temp_hru_path, hruzones_gdb_name)
        hru_gdb_path_underscore = os.path.join(temp_hru_path,
                                               "_" +  hruzones_gdb_name)
        if os.path.exists(hru_gdb_path_underscore):
            hru_gdb_path = hru_gdb_path_underscore

        hruzonesdata_obj.hruzonesgdb = HRUZonesGDB.create(hru_gdb_path,
                                                          user,
                                                          hruzones.aoi,
                                                          hruzonesdata_obj)

        # now import the param.gdb for this HRUZonesData instance
        param_gdb_path = os.path.join(
            temp_hru_path,
            constants.HRU_PARAM_GDB_NAME + constants.GDB_EXT,
        )
        hruzonesdata_obj.paramgdb = ParamGDB.create(param_gdb_path,
                                                    user,
                                                    hruzones.aoi,
                                                    hruzonesdata_obj)

        # lastly import the HRU's xml log file
        hru_XML_path = os.path.join(temp_hru_path, constants.HRU_LOG_FILE)
        hruzonesdata_obj.xml = XML.create(hru_XML_path,
                                          hruzonesdata_obj,
                                          user)

        # save the changes to this HRUZonesData instance and return it
        hruzonesdata_obj.save()
        return hruzonesdata_obj

    def export(self, output_dir, querydate=timezone.now()):
        self.xml.export(output_dir, querydate)
        self.hruzonesgdb.export(output_dir, querydate)
        self.paramgdb.export(output_dir, querydate)


class HRUZones(Directory):
    zones = models.ForeignKey("Zones", related_name="hruzones")

    @property
    def subdirectory_of(self):
        return self.zones.path

    @property
    def _parent_object(self):
        return self.aoi

    @classmethod
    @transaction.atomic
    def create(cls, temp_zones_path, hru_name, zones, user, id=None):
        hruzones_obj = HRUZones(aoi=zones.aoi,
                                name=hru_name,
                                zones=zones,
                                id=id,
                                created_by=user)
        hruzones_obj.save()
        HRUZonesData.create(os.path.join(temp_zones_path, hru_name),
                            hruzones_obj,
                            user)
        return hruzones_obj

    def export(self, output_dir, querydate=timezone.now()):
        super(HRUZones, self).export(output_dir, querydate)
        outpath = os.path.join(output_dir, self.name)
        os.mkdir(outpath)
        versions = self.versions.filter(created_at__lt=querydate)
        latest = versions.latest("created_at")
        latest.export(outpath, querydate)
        return outpath


class Zones(Directory):
    @property
    def subdirectory_of(self):
        return self.aoi.path

    @classmethod
    @transaction.atomic
    def create(cls, input_zones_dir, user, aoi, id=None):
        zones_obj = super(Zones, cls).create(aoi, id=id, created_by=user)

        if os.path.exists(input_zones_dir):
            hruzones = [d for d in os.listdir(input_zones_dir)
                        if os.path.isdir(os.path.join(input_zones_dir, d))]

            for hruzone in hruzones:
                HRUZones.create(input_zones_dir,
                                hruzone,
                                zones_obj,
                                user)

        return zones_obj

    def export(self, output_dir, querydate=timezone.now()):
        super(Zones, self).export(output_dir, querydate)
        outpath = os.path.join(output_dir, self.name)
        os.mkdir(outpath)

        for hruzone in self.hruzones.all():
            hruzone.export(outpath, querydate)

        return outpath

