from __future__ import absolute_import

from django.conf import settings
from django.utils import timezone
from django.contrib.gis.db import models

from ..utils.misc import get_subclasses

from .metaclass import InheritanceMetaclass


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class AOIRelationMixin(models.Model):
    """Generic mixin to provide a relation to the AOI model"""
    aoi = models.ForeignKey("AOI",
                            related_name="%(class)s",
                            on_delete=models.CASCADE)

    class Meta:
        abstract = True


class DateMixin(models.Model):
    """Generic mixin to provide a created and removed datetime tracking
    to a model. Also implements a a querydate validation function for
    date-related export functions."""
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(null=True, blank=True, default=None)
    removed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        get_latest_by = 'created_at'
        abstract = True

    def _validate_querydate(self, querydate):
        if querydate < self.created_at:
            name = self.__class__.__name__
            raise Exception(
                "{} was created after query date.".format(name) +
                " Cannot export {} with the given query date.".format(name)
            )

        if querydate > timezone.now():
            raise Exception(
                "Woah, dude, your query date is like totally in the future." +
                " That is most excellent, but my name isn't Bill nor Ted," +
                " so I don't know the future, brah."
            )

    def save(self, set_modified=True, *args, **kwargs):
        """Overrides the default save method to always update
        the modified date unless explicitly specified otherwise
        """
        if not getattr(self, "created_at", None) == None:
            if set_modified:
                self.modified_at = timezone.now()
        return super(DateMixin, self).save(*args, **kwargs)


class CreatedByMixin(models.Model):
    """Generic mixin to provide user tracking to a model."""
    created_by = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="%(app_label)s_%(class)s_created_by",
        null=True,
        on_delete=models.SET_NULL,
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


class ProxyManager(models.Manager):
    """Model manager class used by the ProxyMixin"""
    def get_queryset(self):
        # build a list of all the subclasses of the class,
        # including itself
        classes = [cls.__name__ for cls in get_subclasses(self.model,
                                                          [self.model])]
        queryset = super(ProxyManager, self).get_queryset()
        return queryset.filter(
            classname__in=classes
        )#.select_related()#.prefetch_related(*self.model._prefetch)


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
    _prefetch = []
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
                     for subclass in get_subclasses(cls)])

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
