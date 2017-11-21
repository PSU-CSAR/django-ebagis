from __future__ import absolute_import

from functools import partial

from django.utils import timezone
from django.contrib.gis.db import models
from django.db.models.query import QuerySet

from ...utils.misc import get_subclasses

from ...models.mixins import DateMixin

from .metaclass import InheritanceMetaclass

from .fields import NullFalseBooleanField


class ActiveQuerySet(QuerySet):
    def deactivate(self):
        for obj in self:
            obj.deactivate()

    def active(self):
        return self.filter(_active=True)

    def inactive(self):
        return self.exclude(_active=True)


class ActiveMixin(models.Model):
    _active = NullFalseBooleanField(default=True)
    objects = ActiveQuerySet.as_manager()

    class Meta:
        abstract = True

    @property
    def active(self):
        return self._active

    def can_deactiveate(self):
        return True

    def deactivate(self):
        # check if we can deactivate, or raise an exception
        if not self.can_deactiveate():
            raise ValueError(
                "ERROR: deactivation validation fails; cannot deactivate"
            )

        # deactivate any children: we recurse through these first, in
        # case any fail we shouldn't get to this object's deactivation
        if hasattr(self, '_children') and self._children:
            for child in self._children:
                child.deactivate()

        # call any clean up tasks if defined
        if hasattr(self, 'cleanup'):
            self.cleanup()

        # set as inactive
        self._active = False
        self.save()


# soft delete modified from
# http://www.akshayshah.org/post/django-soft-deletion/

class SDDateQuerySet(ActiveQuerySet):
    def delete(self):
        dt = timezone.now()
        for obj in self:
            obj.delete(datetime=dt)

    def hard_delete(self):
        for obj in self:
            obj.hard_delete()

    def not_removed(self):
        return self.filter(removed_at__isnull=True)

    def removed(self):
        return self.exclude(removed_at__isnull=True)

    def archived(self):
        return self.removed().inactive()

    def current(self):
        return self.not_removed().active()


class SDDateMixin(ActiveMixin, DateMixin):
    """Generic mixin overriding model delete handling to
    provide a soft-delete functionality for archival purposes."""
    objects = SDDateQuerySet.as_manager()

    class Meta:
        abstract = True

    @property
    def removed(self):
        return self.removed_at is not None

    @property
    def current(self):
        return self.active and not self.removed

    def delete(self, datetime=timezone.now()):
        if hasattr(self, '_children') and self._children:
            for child in self._children:
                child.delete()
        self.removed_at = datetime
        self.save()

    def hard_delete(self):
        super(SDDateMixin, self).delete()

    def can_deactiveate(self):
        return self.removed_at is not None


def proxy_get_queryset(self, klass):
    '''build a list of all the subclasses of the class,
    including itself'''
    classes = [cls.__name__ for cls in get_subclasses(self.model,
                                                      [self.model])]
    queryset = super(klass, self).get_queryset()
    return queryset.filter(
        classname__in=classes
    )


class SDDateProxyManager(models.Manager):
    def get_queryset(self):
        return proxy_get_queryset(self, klass=SDDateProxyManager)


class SDDateProxyMixin(SDDateMixin, models.Model):
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
    objects = SDDateProxyManager.from_queryset(SDDateQuerySet)()

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
        return super(SDDateProxyMixin, self).save(*args, **kwargs)

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
