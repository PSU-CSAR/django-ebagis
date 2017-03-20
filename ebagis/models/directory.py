from __future__ import absolute_import

import os
import shutil
import glob
import errno
import logging

from itertools import chain

from django.contrib.gis.db import models
from django.utils import timezone

from ..utils import transaction
from .. import constants

from .base import ABC
from .file import File
from .mixins import (
    ProxyMixin, DateMixin, NameMixin, AOIRelationMixin, CreatedByMixin
)


logger = logging.getLogger(__name__)


class DirectoryManager(models.Manager):
    """Model manager class used by the Directory Class"""
    def get_queryset(self):
        return super(DirectoryManager, self).get_queryset(
            ).select_related()#.prefetch_related(*self.model._prefetch)


class Directory(ProxyMixin, DateMixin, NameMixin, CreatedByMixin,
                AOIRelationMixin, ABC):
    _CREATE_DIRECTORY_ON_EXPORT = True
    _prefetch = []
    _path_name = None

    _archive_fields = {"read_only": ["id", "created_at", "created_by"],
                       "writable": ["name", "comment"]}

    archiving_rule = models.CharField(max_length=10,
                                      choices=constants.ARCHIVING_CHOICES,
                                      default=constants.NO_ARCHIVING,
                                      editable=False)
    parent_directory = models.CharField(max_length=1000)
    _parent_object = models.ForeignKey('self',
                                       related_name='subdirectories',
                                       null=True,
                                       blank=True,
                                       on_delete=models.CASCADE)

    class Meta:
        unique_together = ("_parent_object", "name")

    @property
    def parent_object(self):
        return self._parent_object

    @property
    def subdirectory_of(self):
        return self._parent_object.path

    @property
    def _metadata_path(self):
        """overriding this property to put the metadata file in the
        directory above the directory represented by this object
        """
        # I don't think this object could ever represent the root
        # of a disk, so I believe this property will always return
        # a reasonable value
        return self.parent_directory

    @property
    def _filesystem_name(self):
        """this property is the name of the file system dir
        that gets created when an instance is first saved
        we simply default to using the value of the
        "name" field, though this method can be overridden
        to change what field/value subclasses use
        """
        return self.name

    def save(self, *args, **kwargs):
        """Overrides the default save method adding the following:

        - if the path has not been set:
            - sets the created at time
            - set the path property to ensure a file system directory
              is created for this directory object within its
              enclosing file system folder
        """
        if not getattr(self, 'parent_directory', None):
            # while a default created_at datetime is set by the
            # date mixin, we have to explictly set the created_at
            # datetime here, as it is required by the path method
            # when creating the new directory and only would be set
            # by default when the save method is called (after the
            # path method has already been called)
            now = timezone.now()
            self.created_at = now
            self.path
        return super(Directory, self).save(*args, **kwargs)

    def delete(self, delete_file=True, *args, **kwargs):
        """Overrides the default delete method adding the following:

         - removes the directory at the path from the file system"""
        if delete_file:
            import shutil
            try:
                shutil.rmtree(self.path)
            except (IOError, OSError) as e:
                # check to see if the error was
                # that the dir is already gone
                if e.errno != errno.ENOENT:
                    raise e
        return super(Directory, self).delete(*args, **kwargs)

    @property
    def path(self):
        """On first run, creates the directory for the model
        returning the path of the created directory. If already
        set, returns the directory path from the parent_directory
        and the object's name."""

        # check to see if path property is set
        if not getattr(self, 'parent_directory', None):
            # default path is simply the value of the name field
            # inside the subdirectory_of path
            path = os.path.join(self.subdirectory_of, self._filesystem_name)

            # if archiving rule set to group archiving, then the
            # directory name need needs the date appended
            if self.archiving_rule == constants.GROUP_ARCHIVING:
                path += self.created_at.strftime("_%Y%m%d%H%M%S")

            # try to create the directory
            try:
                os.makedirs(path)
            except Exception as e:
                logger.exception("Failed create directory: {}".format(path))
                raise e
            else:
                # set the value of the directory path field
                self.parent_directory = self.subdirectory_of

        return os.path.join(self.parent_directory, self._filesystem_name)

    @classmethod
    @transaction.atomic
    def create(cls, import_dir, parent_object, user,
               name=None, id=None, comment=""):
        from .aoi import AOI

        if not name:
            name = cls._path_name if cls._path_name else cls.__name__.lower()

        if isinstance(parent_object, AOI):
            aoi = parent_object
            parent_object = None
        else:
            aoi = parent_object.aoi

        dir_obj = cls(aoi=aoi,
                      name=name,
                      id=id,
                      _parent_object=parent_object,
                      created_by=user,
                      comment=comment)

        # save actually creates the dir on disk
        dir_obj.save()

        try:
            # now we can add the content
            # override the import_content method on proxy classes
            # to define what content is actually imported
            dir_obj.import_content(import_dir)

        except Exception as e:
            try:
                if dir_obj.path:
                    shutil.rmtree(dir_obj.path)
            except Exception as e2:
                logger.exception(e2)
                logger.exception(
                    "Failed to remove directory on import error: {}"
                    .format(dir_obj.path)
                )
            raise e

        return dir_obj

    def import_content(self, directory_to_import):
        '''This method is called in by the create method to
        import all managed subdirectories and files into the
        database. The base method here could look something like
        this (in pseudocode):

        for dir in directory_to_import:
            Directory.create(dir, parent_object=self)

        for file in directory_to_import:
            File.create(file, parent_object=self)

        However, we have decided that we do not want users to be
        able to put in any content they desire. As such, we only
        want to import specific files from each directory (and
        each directory has been implemented as a proxy model of
        this Directory class). So we can override this method on
        those proxy classes and specifically define what files/dirs
        get imported, and importantly, what proxy models to use for
        each one.'''
        raise NotImplementedError

    def export(self, output_dir, querydate=timezone.now(), outname=None):
        self._validate_querydate(querydate)

        # create the output dir for this object
        if self._CREATE_DIRECTORY_ON_EXPORT:
            outname = outname if outname else self.name
            output_dir = os.path.join(output_dir, outname)
            os.mkdir(output_dir)

        self.export_content(output_dir, querydate=querydate)

        return output_dir

    def export_content(self, output_dir, querydate=timezone.now()):
        # export all of this object's content into the output dir
        for obj in chain(self.subdirectories.all(), self.files.all()):
            obj.export(output_dir, querydate)

    @transaction.atomic
    def update(self):
        raise NotImplementedError


class Maps(Directory):
    class Meta:
        proxy = True

    _prefetch = ["maps"]

    @property
    def mapdocs(self):
        return self.files.filter(name__endswith=constants.MAP_EXT)

    @property
    def analysis_xml(self):
        return self.files.get(name=constants.MAP_ANALYSISXML_FILE)

    @property
    def map_parameters_txt(self):
        return self.files.get(name=constants.MAP_PARAMTXT_FILE)

    def import_content(self, directory_to_import):
        for mapdoc in glob.glob(
                os.path.join(directory_to_import, "*" + constants.MAP_EXT)
        ):
            File.create(mapdoc, self, self.created_by)

        other_files = [
             os.path.join(directory_to_import, constants.MAP_ANALYSISXML_FILE),
             os.path.join(directory_to_import, constants.MAP_PARAMTXT_FILE),
        ]

        for _file in other_files:
            File.create(_file, self, self.created_by)


class PrismDir(Directory):
    class Meta:
        proxy = True

    _prefetch = ["versions"]
    _singular = True
    _path_name = constants.PRISM_DIR_NAME

    @property
    def versions(self):
        return self.subdirectories.filter(classname='Prism')

    def import_content(self, directory_to_import):
        from .geodatabase import Prism
        prism_gdb = os.path.join(directory_to_import, constants.PRISM_GDB)
        Prism.create(prism_gdb, self, self.created_by)

    def export_content(self, output_dir, querydate=timezone.now()):
        filtered = self.versions.filter(created_at__lt=querydate)
        filtered.latest("created_at").export(output_dir,
                                             querydate=querydate)
