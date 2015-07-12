from __future__ import absolute_import
import os

from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.gis.db import models

from .. import constants

from .metaclass import InheritanceMetaclass


# ***************** MIXINS *****************

class AOIRelationMixin(models.Model):
    """Generic mixin to provide a relation to the AOI model"""
    aoi = models.ForeignKey("AOI", related_name="%(class)s_related")

    class Meta:
        abstract = True


class DateMixin(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    removed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        get_latest_by = 'created_at'
        abstract = True

    def _valid_querydate(self, querydate):
        if querydate < self.created_at:
            raise Exception(
                "AOI was created after query date." +
                " Cannot export AOI state for the given query date."
            )

        if querydate > timezone.now():
            raise Exception(
                "Woah, dude, your query date is like totally in the future." +
                " That is most excellent, but my name isn't Bill nor Ted," +
                " so I don't know the future, brah."
            )

    def export(self, output_dir, querydate, *args, **kwargs):
        self._valid_querydate(querydate)


class CreatedByMixin(models.Model):
    created_by = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_created_by"
    )

    class Meta:
        abstract = True


class NameMixin(models.Model):
    """Generic Mixin to provide a standarized name field"""
    name = models.CharField(max_length=100)

    def __unicode__(self):
        """When getting the string representation of this
        object in Django, use the name field"""
        return self.name

    class Meta:
        abstract = True


class UniqueNameMixin(models.Model):
    """Generic Mixin to provide a standarized
    name field with unique constraint"""
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        """When getting the string representation of this
        object in Django, use the name field"""
        return self.name

    class Meta:
        abstract = True


class DirectoryMixin(DateMixin, NameMixin, models.Model):
    """Mixin providing directory creation and deletion to
    directory-type models."""
    _path = models.CharField(max_length=1000,
                             db_column="path")
    archiving_rule = models.CharField(max_length=10,
                                      choices=constants.ARCHIVING_CHOICES,
                                      default=constants.NO_ARCHIVING,
                                      editable=False)
    subdirectory_of = os.getcwd()

    class Meta:
        unique_together = ("subdirectory_of", "name")
        abstract = True

    def save(self, *args, **kwargs):
        """Overrides the default save method adding the following:

         - if the object has not been saved (no pk set),
           sets the created at time and calls for the path
           property to ensure a directory is created for the
           GDB within its enclosing AOI"""
        if not self.pk:
            self.created_at = timezone.now()
            self.path
        return super(DirectoryMixin, self).save(*args, **kwargs)

    def delete(self, delete_file=True, *args, **kwargs):
        """Overrides the default delete method adding the following:

         - removes the directory at the path from the file system"""
        if delete_file:
            import shutil
            if os.path.exists(self.path):
                shutil.rmtree(self.path)
        return super(DirectoryMixin, self).delete(*args, **kwargs)

    @property
    def path(self):
        """On first run, creates the directory for a directory-using
        model, returning the path of the created directory. If already
        set, simply returns the directory path."""

        # check to see if path property is set
        if not getattr(self, '_path', None):
            # default path is simply the value of the name field
            # inside the subdirectory_of path
            path = os.path.join(self.subdirectory_of, self.name)

            # if archiving rule set to group archiving, then the
            # directory name need needs the date appended
            if self.archiving_rule == constants.GROUP_ARCHIVING:
                path += self.created_at.strftime("_%Y%m%d%H%M%S")

            # try to create the directory
            try:
                os.makedirs(path)
            except Exception as e:
                print "Failed create directory: {}".format(path)
                raise e
            else:
                # set the value of the directory path field
                self._path = path

        return self._path

    # I hate this name but what are you going to do--can't use import
    @classmethod
    def create(cls, *args, **kwargs):
        raise NotImplementedError
        # I think this can be a generic function for the class...
        # No, it can't, as arcpy functions must be used in geodatabases...
        # I may implement it here and then override it in the geodatabase...
        # name should default to the name of the directory, but geodatabases
        # will need to strip the .gdb...
        # With more thought, this really is as complex and specific as the
        # export methods -- need to implement each subclass individually.

    def export(self, output_dir, querydate, *args, **kwargs):
        super(DirectoryMixin, self).export(output_dir,
                                           querydate,
                                           *args,
                                           **kwargs)


class ProxyManager(models.Manager):
    def get_queryset(self):
        classes = [cls.__name__ for cls in _get_subclasses(self.model,
                                                           [self.model])]
        queryset = super(ProxyManager, self).get_queryset()
        return queryset.filter(classname__in=classes)


def _get_subclasses(Class, list_of_subclasses=[]):
    for subclass in Class.__subclasses__():
        list_of_subclasses.append(subclass)
        list_of_subclasses = _get_subclasses(subclass, list_of_subclasses)
    return list_of_subclasses


class ProxyMixin(models.Model):
    """Generic Mixin to provide full support to proxy classes
    for returning and saving objects of subclasses to the base
    class.

    NOTE: Using the proxy mixin requires that it be the first
    class inherited from in any subclasses. Failing to follow
    this requirement will likely break the custom manager class
    such that the correct class types will not be returned."""
    __metaclass__ = InheritanceMetaclass
    classname = models.CharField(max_length=40)
    objects = ProxyManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Overrides the default save method to do the following:

         - automatically assign the classname of the instance
           to be that of the class of which it is an
           instance. In other words, a Maps instance
           will be saved with the classname 'Maps'"""
        if not self.classname:
            self.classname = self.__class__.__name__
        return super(ProxyMixin, self).save(*args, **kwargs)

    @classmethod
    def get_subclasses(cls):
        """Finds all subclasses of the current object's class.
        Used in the get_object method to return object as a
        specific subclass object, if nessesary."""
        return dict([(subclass.__name__, subclass)
                     for subclass in _get_subclasses(cls)])

    def get_object(self):
        """Ensures when getting an object, it will be of
        the same type as it was created, e.g., the type
        of directory as indicated by its name."""
        subclasses = self.get_subclasses()
        # check to see if the class name in the db is
        # a subclass of the current class; if yes,
        # change the class of the returned object to
        # the subclass else return the current class
        if self.classname in subclasses:
            self.__class__ = subclasses[self.classname]
        return self
