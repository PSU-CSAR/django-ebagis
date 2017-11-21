from __future__ import absolute_import

from django.conf import settings
from django.utils import timezone
from django.contrib.gis.db import models


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class AOIRelationMixin(models.Model):
    """Generic mixin to provide a relation to the AOI model"""
    aoi = models.ForeignKey("AOI",
                            related_name="%(class)s",
                            on_delete=models.CASCADE)

    class Meta:
        abstract = True


class DateMixin(models.Model):
    """Generic mixin to provide a created, modified, and removed
    datetime tracking. The mixin also implements a querydate
    validation function for date-related export functions."""
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
        if not getattr(self, "created_at", None) == None and set_modified:
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
