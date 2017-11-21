from __future__ import absolute_import
import os

from django.conf import settings
from django.utils import timezone

from ebagis import constants
from ebagis.utils import transaction
from ebagis.utils.itertools import chain


from .directory import Directory
from .geodatabase import Surfaces, Layers, AOIdb, Analysis
from .directory import PrismDir, Maps
from .zones import Zones


class AOIDirectory(Directory):
    class Meta:
        proxy = True

    _archive_fields = {
        "read_only": ["id", "created_at", "created_by",
                      "surfaces", "layers", "aoidb", "_prism", "analysis",
                      "maps", "_zones"],
        "writable": ["name", "comment"]
    }

    # we want to put AOI directoies in the
    # location specified in the settings
    subdirectory_of = settings.AOI_DIRECTORY

    @property
    def _metadata_path(self):
        """again overriding this property to put the metadata file
        inside the AOI directory. While this conflicts with all other
        directory subclasses, I believe the case of the AOI object
        is different enough to warrant this change.
        """
        return self.path

    @property
    def _filesystem_name(self):
        """This property is the name of the file system directory
        created when an AOI instance is saved.

        Here we use the ID and not the name so we can do two things:
            1) allow multiple AOIs with the same name (though this
               is currently prevented with a database constraint)
            2) change the name of an existing AOI and not have to change
               anything in the file system (except the metadata file)
        """
        return str(self.id)

    @property
    def _archive_name(self):
        """Again we override per a special case of the AOIDirectory
        class, in that the archive of this directory should just be the
        name of the parent AOI.
        """
        return self.aoi.name

    @property
    def aoi_path(self):
        """The aoi_path property is used to construct paths to resources
        relative to the parent AOI's directory. The AOIDirectory has a
        special case, in that it should represent the root of the AOI,
        and should have the name of the AOI. Thus we override here and
        grab the name of the parent AOI per its aoi_path method.
        """
        return self.aoi.aoi_path

    @property
    def parent_object(self):
        return self.aoi

    @property
    def surfaces(self):
        return self.subdirectories.get(classname='Surfaces')

    @property
    def layers(self):
        return self.subdirectories.get(classname='Layers')

    @property
    def aoidb(self):
        return self.subdirectories.get(classname='AOIdb')

    @property
    def analysis(self):
        return self.subdirectories.get(classname='Analysis')

    @property
    def _prism(self):
        return self.subdirectories.get(classname='PrismDir')

    @property
    def prism(self):
        return self._prism.versions.current()

    @property
    def maps(self):
        return self.subdirectories.get(classname='Maps')

    @property
    def _zones(self):
        return self.subdirectories.get(classname='Zones')

    @property
    def zones(self):
        return self._zones.hruzones.current()

    @property
    def items(self):
        return list(chain([
            self.surfaces,
            self.layers,
            self.aoidb,
            self.analysis,
            self._prism,
            self.maps,
            self._zones,
        ]))

    # the _all versions don't filter inactive/removed records
    @property
    def surfaces_all(self):
        return self._subdirectories.get(classname='Surfaces')

    @property
    def layers_all(self):
        return self._subdirectories.get(classname='Layers')

    @property
    def aoidb_all(self):
        return self._subdirectories.get(classname='AOIdb')

    @property
    def analysis_all(self):
        return self._subdirectories.get(classname='Analysis')

    @property
    def _prism_all(self):
        return self._subdirectories.get(classname='PrismDir')

    @property
    def prism_all(self):
        return self._prism_all.versions.all()

    @property
    def maps_all(self):
        return self._subdirectories.get(classname='Maps')

    @property
    def _zones_all(self):
        return self._subdirectories.get(classname='Zones')

    @property
    def zones_all(self):
        return self._zones_all.hruzones.all()

    @property
    def items_all(self):
        return list(chain([
            self.surfaces_all,
            self.layers_all,
            self.aoidb_all,
            self.analysis_all,
            self._prism_all,
            self.maps_all,
            self._zones_all,
        ]))

    @property
    def _children(self):
        return self.items_all

    def import_content(self, temp_aoi_path):
            # import aoi.gdb
            AOIdb.create(
                os.path.join(temp_aoi_path,
                             constants.AOI_GDB),
                self,
                self.created_by,
            )

            # import surfaces.gdb
            Surfaces.create(
                os.path.join(temp_aoi_path,
                             constants.SURFACES_GDB),
                self,
                self.created_by,
            )

            # import layers.gdb
            Layers.create(
                os.path.join(temp_aoi_path,
                             constants.LAYERS_GDB),
                self,
                self.created_by,
            )

            # import HRU Zones
            Zones.create(
                os.path.join(temp_aoi_path,
                             constants.ZONES_DIR_NAME),
                self,
                self.created_by,
            )

            # import analysis.gdb
            Analysis.create(
                os.path.join(temp_aoi_path,
                             constants.ANALYSIS_GDB),
                self,
                self.created_by,
            )

            # import prism.gdb
            PrismDir.create(
                os.path.join(temp_aoi_path,
                             constants.PRISM_GDB),
                self,
                self.created_by,
            )

            # import param.gdb

            # import loose files in param/

            # import param/paramdata.gdb

            # import map docs in maps directory
            Maps.create(
                os.path.join(temp_aoi_path,
                             constants.MAPS_DIR),
                self,
                self.created_by,
            )

    @transaction.atomic
    def update(self):
        raise NotImplementedError

    def export_content(self, output_dir, querydate=timezone.now()):
        self.surfaces.export(output_dir, querydate=querydate)
        self.layers.export(output_dir, querydate=querydate)
        self.aoidb.export(output_dir, querydate=querydate)
        self.analysis.export(output_dir, querydate=querydate)
        self._prism.export(output_dir, querydate=querydate)
        self.maps.export(output_dir, querydate=querydate)
        self._zones.export(output_dir, querydate=querydate)

    def get_url(self, request):
        return self.aoi.get_url(request)
