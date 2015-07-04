from __future__ import absolute_import
import os

from django.utils import timezone
from django.contrib.gis.db import models
from django.db import transaction

from ebagis import constants

from .directory import Directory
from .mixins import CreatedByMixin
from .geodatabase import HRUZonesGDB
from .file import XML


class HRUZonesData(CreatedByMixin, Directory):
    xml = models.OneToOneField(XML, related_name="hru_xml")
    hruzonesgdb = models.OneToOneField("HRUZonesGDB",
                                       related_name="hru_hruGDB")
    hruzones = models.ForeignKey("HRUZones", related_name="versions")

    def __init__(self, *args, **kwargs):
        # override default NO_ARCHIVING with GROUP_ARCHIVING rule
        self._meta.get_field('archiving_rule').default = \
            constants.GROUP_ARCHIVING
        super(HRUZones, self).__init__(*args, **kwargs)

    @property
    def subdirectory_of(self):
        return self.hru.path

    @classmethod
    @transaction.atomic
    def create(cls, temp_hru_path, hruzones, user):
        hruzonesdata_obj = HRUZones(aoi=hruzones.aoi,
                                    name=hruzones.name,
                                    hruzones=hruzones,
                                    created_by=user)
        hruzonesdata_obj.save()
        hru_gdb_path = os.path.join(temp_hru_path,
                                    hruzones.name,
                                    constants.GDB_EXT)
        hruzonesdata_obj.hruzonesgdb = HRUZonesGDB.create(hru_gdb_path,
                                                          hruzones.aoi,
                                                          user)
        hru_XML_path = os.path.join(temp_hru_path, constants.HRU_LOG_FILE)
        hruzonesdata_obj.xml = XML.create(hru_XML_path,
                                          hruzonesdata_obj,
                                          hruzones.aoi,
                                          user)
        hruzonesdata_obj.save()
        return hruzonesdata_obj

    def export(self, output_dir):
        self.xml.export(output_dir)
        self.hruzones.export(output_dir)


class HRUZones(Directory):
    zones = models.ForeignKey("Zones", related_name="hruzones")

    @property
    def subdirectory_of(self):
        return self.zones.path

    @classmethod
    @transaction.atomic
    def create(cls, temp_zones_path, hru_name, zones, user):
        hruzones_obj = HRUZones(aoi=zones.aoi,
                                name=hru_name,
                                zones=zones)
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
        latest.xml.export(outpath)
        latest.hruzones.export(outpath)
        return outpath


class Zones(Directory):
    @property
    def subdirectory_of(self):
        return self.aoi.path

    @classmethod
    @transaction.atomic
    def create(cls, input_zones_dir, user, aoi):
        zones_obj = super(Zones, cls).create(aoi)

        if os.path.exists(input_zones_dir):
            hruzones = [d for d in os.listdir(input_zones_dir)
                        if os.path.isdir(d)]

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
