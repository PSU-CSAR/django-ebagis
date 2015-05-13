from __future__ import absolute_import
import os
import shutil
from logging import exception

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.base import ModelBase
from django.utils import timezone

from djcelery.models import TaskMeta

from drf_chunked_upload.models import ChunkedUpload

from .constants import NO_ARCHIVING, LAYER_ARCHIVING, GROUP_ARCHIVING,\
    ARCHIVING_CHOICES

from .settings import AOI_DIRECTORY, GEO_WKID


"""
A new base class for Django models, which provides them with a better and random
looking primary key for the 'id' field.
This solves the problem of having predictable, sequentially numbered primary keys
for Django models.
Just use 'RandomPrimaryIdModel' as base class for your Django models. That's all.
The generated keys look similar to what you know from URL shorteners. Here are some
examples:
    Ada6z
    UFLX1
    Q68mf
    zjvsx3
    fDXshK
    VNuL0Lp
Each character in the key may be a letter (upper and lower case) or a digit, except
the first chracter, which is always a letter. Therefore, with any additional character
in the key length, the key space increases 62 fold. Just 5 characters already give you
more than 768 million different keys. As the key space gets tighter (can't find unused
key after a few tries), the key length is being increased.
The starting key length and maximum key length are tunable.
License: Use as you wish, for whatever purpose. If you have any improvement or ideas,
         it would be nice if you could share those.
DISCLAIMER: THE WORKS ARE WITHOUT WARRANTY
(c) 2012 Juergen Brendel (http://brendel.com/consulting)
"""

import string
import random

from django.db.utils import IntegrityError
from django.contrib.gis.db import models
from django.db import transaction

class RandomPrimaryIdModel(models.Model):
    """
    An abstract base class, which provides a random looking primary key for Django models.
    The save() call is pre-processed in order to come up with a different, more random looking
    ID field in order to avoid guessable IDs or the leaking of information to the end user if
    primary keys are ever used in an exposed context. One can always use an internal ID and
    have an additional, random looking exposed ID. But then you'd have to replicate the effort
    anyway, so we may just as well create a properly random looking primary key.
    The performance impact of this doesn't seem to be too bad: We have to call random.choice()
    a couple of times to create a key. If the newly chosen random key does not exist in the
    database then we just save it and are done. Only in case of collision will we have to create
    a new key and retry.
    We retry a number of times, slowly increasing the key length (starting at CRYPT_KEY_LEN_MIN
    and going all the way up to CRYPT_KEY_LEN_MAX). At each key-length stage we try a number
    of times (as many times as the key is long, actually). If we still can't find an unused
    unique key after all those tries we give up with an exception. Note that we do not ex-
    haustively search the key space.
    In reality, getting any sort of collision will be unlikely to begin with. The default
    starting key length of 5 characters will give you more than 768 million unique keys. You
    won't get all of them, but after 5 failed tries, you will jump to 6 characters (now you
    have 62 times more keys to choose from) and likely will quickly find an available key.
    Usage:
    Base your models on RandomPrimaryIdModel, rather than models.Model. That's all.
    Then use CRYPT_KEY_LEN_MIN, CRYPT_KEY_LEN_MAX, KEYPREFIX and KEYSUFFIX in your model's
    class definition to tune the behaviour of the primary key.
    If smaller keys are important to you, decrease the CRYPT_KEY_LEN_MIN value, maybe to
    three. If less retries during possible collisions are important to you and you don't
    mind a few more characters in the key, increase CRYPT_KEY_LEN_MIN and maybe also the
    value for CRYPT_KEY_LEN_MAX.
    Use KEYPREFIX and KEYSUFFIX to specify custom prefixes and suffixes for the key. This
    gives you the option to visually distinguish the keys of different models, if you should
    ever need that. By default, both of those are "".
    Use _FIRSTIDCHAR and _IDCHAR to tune the characters that may appear in the key.
    """
    KEYPREFIX         = ""
    KEYSUFFIX         = ""
    CRYPT_KEY_LEN_MIN = 5
    CRYPT_KEY_LEN_MAX = 9
    _FIRSTIDCHAR      = string.ascii_letters                  # First char: Always a letter
    _IDCHARS          = string.digits + string.ascii_letters  # Letters and digits for the rest

    """ Our new ID field """
    id = models.CharField(db_index    = True,
                          primary_key = True,
                          max_length  = CRYPT_KEY_LEN_MAX+1+len(KEYPREFIX)+len(KEYSUFFIX),
                          unique      = True,
                          editable    = False)

    def __init__(self, *args, **kwargs):
        """
        Nothing to do but to call the super class' __init__ method and initialize a few vars.
        """
        super(RandomPrimaryIdModel, self).__init__(*args, **kwargs)
        self._retry_count = 0    # used for testing and debugging, nothing else

    def _make_random_key(self, key_len):
        """
        Produce a new unique primary key.
        This ID always starts with a letter, but can then have numbers
        or letters in the remaining positions.
        Whatever is specified in KEYPREFIX or KEYSUFFIX is pre/appended
        to the generated key.
        """
        return self.KEYPREFIX + random.choice(self._FIRSTIDCHAR) + \
               ''.join([ random.choice(self._IDCHARS) for dummy in xrange(0, key_len-1) ]) + \
               self.KEYSUFFIX

    def save(self, *args, **kwargs):
        """
        Modified save() function, which selects a special unique ID if necessary.
        Calls the save() method of the first model.Models base class it can find
        in the base-class list.
        """
        if self.id:
            # Apparently, we know our ID already, so we don't have to
            # do anything special here.
            super(RandomPrimaryIdModel, self).save(*args, **kwargs)
            return

        try_key_len                     = self.CRYPT_KEY_LEN_MIN
        try_since_last_key_len_increase = 0
        while try_key_len <= self.CRYPT_KEY_LEN_MAX:
            # Randomly choose a new unique key
            _id = self._make_random_key(try_key_len)
            sid = transaction.savepoint()       # Needed for Postgres, doesn't harm the others
            try:
                if kwargs is None:
                    kwargs = dict()
                kwargs['force_insert'] = True           # If force_insert is already present in
                                                        # kwargs, we want to make sure it's
                                                        # overwritten. Also, by putting it here
                                                        # we can be sure we don't accidentally
                                                        # specify it twice.
                self.id = _id
                super(RandomPrimaryIdModel, self).save(*args, **kwargs)
                break                                   # This was a success, so we are done here

            except IntegrityError, e:                   # Apparently, this key is already in use
                # Only way to differentiate between different IntegrityErrors is to look
                # into the message string. Too bad. But I need to make sure I only catch
                # the ones for the 'id' column.
                #
                # Sadly, error messages from different databases look different and Django does
                # not normalize them. So I need to run more than one test. One of these days, I
                # could probably just examine the database settings, figure out which DB we use
                # and then do just a single correct test.
                #
                # Just to complicates things a bit, the actual error message is not always in
                # e.message, but may be in the args of the exception. The args list can vary
                # in length, but so far it seems that the message is always the last one in
                # the args list. So, that's where I get the message string from. Then I do my
                # DB specific tests on the message string.
                #
                msg = e.args[-1]
                if msg.endswith("for key 'PRIMARY'") or msg == "column uuid is not unique" or \
                        "Key (id)=" in msg:
                    transaction.savepoint_rollback(sid) # Needs to be done for Postgres, since
                                                        # otherwise the whole transaction is
                                                        # cancelled, if this is part of a larger
                                                        # transaction.

                    self._retry_count += 1              # Maintained for debugging/testing purposes
                    try_since_last_key_len_increase += 1
                    if try_since_last_key_len_increase == try_key_len:
                        # Every key-len tries, we increase the key length by 1.
                        # This means we only try a few times at the start, but then try more
                        # and more for larger key sizes.
                        try_key_len += 1
                        try_since_last_key_len_increase = 0
                else:
                    # Some other IntegrityError? Need to re-raise it...
                    raise e

        else:
            # while ... else (just as a reminder): Execute 'else' if while loop is exited normally.
            # In our case, this only happens if we finally run out of attempts to find a key.
            self.id = None
            raise IntegrityError("Could not produce unique ID for model of type %s" % type(self))

    class Meta:
        abstract = True


# ************** METACLASSES ***************

class InheritanceMetaclass(ModelBase):
    """Allows a model to return the subclass types from
    the name field. That is, if you want a Surfaces geodatabase,
    where Surfaces is a proxy of the Geodatabase class, you'll
    get a Surfaces instance, not a Geodatabase instance.

    Used with the ProxyMixin."""
    def __call__(cls, *args, **kwargs):
        obj = super(InheritanceMetaclass, cls).__call__(*args, **kwargs)
        return obj.get_object()


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
    _directory_path = models.CharField(max_length=1000,
                                       db_column="directory_path")
    archiving_rule = models.CharField(max_length=5,
                                      choices=ARCHIVING_CHOICES,
                                      default=NO_ARCHIVING,
                                      editable=False)
    subdirectory_of = os.getcwd()

    class Meta:
        unique_together = ("subdirectory_of", "name")
        abstract = True

    def save(self, *args, **kwargs):
        """Overrides the default save method adding the following:

         - if the object has not been saved (no pk set),
           sets the created at time and calls for the directory_path
           property to ensure a directory is created for the
           GDB within its enclosing AOI"""
        if not self.pk:
            self.created_at = timezone.now()
            self.directory_path
        return super(DirectoryMixin, self).save(*args, **kwargs)

    def delete(self, delete_file=True, *args, **kwargs):
        """Overrides the default delete method adding the following:

         - removes the directory at directory path from the file system"""
        if delete_file:
            import shutil
            if os.path.exists(self.directory_path):
                shutil.rmtree(self.directory_path)
        return super(DirectoryMixin, self).delete(*args, **kwargs)

    @property
    def directory_path(self):
        """On first run, creates the directory for a directory-using
        model, returning the path of the created directory. If already
        set, simply returns the directory path."""

        # check to see if directory path property is set
        if not getattr(self, '_directory_path', None):
            # default path is simply the value of the name field
            # inside the subdirectory_of path
            path = os.path.join(self.subdirectory_of, self.name)

            # if archiving rule set to group archiving, then the
            # directory name need needs the date appended
            if self.archiving_rule == GROUP_ARCHIVING:
                path += self.created_at.strftime("_%Y%m%d%H%M%S")

            # try to create the directory
            try:
                os.makedirs(path)
            except Exception as e:
                print "Failed create directory: {}".format(path)
                raise e
            else:
                # set the value of the directory path field
                self._directory_path = path

        return self._directory_path

    def export(self):
        raise NotImplementedError


class ProxyManager(models.Manager):
    def get_queryset(self):
        classes = [subclass.__name__ for subclass in self.model.__subclasses__()]
        classes.append(self.model._meta.object_name)
        return super(ProxyManager, self).get_queryset().filter(classname__in=classes)


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

         - automatically assign the name based on the name of
           the instance to be that of the class of which it is
           an instance. In other words, a Maps instace
           will be saved with the name of 'Maps'"""
        if not self.classname:
            self.classname = self.__class__.__name__
        return super(ProxyMixin, self).save(*args, **kwargs)

    @classmethod
    def get_subclasses(cls):
        """Finds all subclasses of the current object's class.
        Used in the get_object method to return object as a
        specific subclass object, if nessesary."""
        return dict([(subclass.__name__, subclass)
                     for subclass in cls.__subclasses__()])

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


# *************** FILE CLASSES ***************

class FileData(ProxyMixin, DateMixin, CreatedByMixin,
               AOIRelationMixin, RandomPrimaryIdModel):
    filepath = models.CharField(max_length=1024)
    filename = models.CharField(max_length=255)
    encoding = models.CharField(max_length=20, null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=10)
    content_object = GenericForeignKey('content_type', 'object_id')

    def export(self, output_dir):
        shutil.copy2(self.filepath, os.path.join(output_dir, self.filename))

# "Data" types must match their enclosing layer type, e.g., a vector
# data instance can only relate to a vector layer instance. Thus,
# each type needs to have the content type choices limited to
# restrict allowable relations to the appropriate class.
FileData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'file'}


class XMLData(FileData):
    class Meta:
        proxy = True

XMLData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'xml'}


class VectorData(FileData):
#    srs_wkt = models.CharField(max_length=1000)
#    geom_type = models.CharField(max_length=50)

    class Meta:
        proxy = True

    def export(self, output_dir):
        from arcpy.management import CopyFeatures
        CopyFeatures(self.filepath, os.path.join(output_dir, self.filename))

VectorData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'vector'}


class RasterData(FileData):
    #srs_wkt = models.CharField(max_length=1000)
    #resolution = models.FloatField()

    class Meta:
        proxy = True

    def export(self, output_dir):
        from arcpy.management import CopyRaster
        CopyRaster(self.filepath, os.path.join(output_dir, self.filename))

RasterData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'raster'}


class TableData(FileData):
    class Meta:
        proxy = True


    def export(self, output_dir):
        from arcpy.management import CopyRows
        CopyRows(self.filepath, os.path.join(output_dir, self.filename))

TableData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'table'}


class MapDocumentData(FileData):
    class Meta:
        proxy = True

MapDocumentData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'mapdocument'}


# ************* LAYER CLASSES **************

class File(ProxyMixin, DateMixin, NameMixin, AOIRelationMixin,
           RandomPrimaryIdModel):
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=10)
    content_object = GenericForeignKey('content_type', 'object_id')
    versions = GenericRelation(FileData, for_concrete_model=False)

    class Meta:
        unique_together = ("content_type", "object_id", "name")

    def export(self, output_dir, version_id=None):
        if version_id:
            return self.versions.get(id=version_id).export(output_dir)
        else:
            return self.versions.latest("created_at").export(output_dir)


class XML(File):
    class Meta:
        proxy = True


class Vector(File):
    class Meta:
        proxy = True


class Raster(File):
    class Meta:
        proxy = True


class Table(File):
    class Meta:
        proxy = True


class MapDocument(File):
    class Meta:
        proxy = True


# *********** DIRECTORY CLASSES ************

class Directory(DirectoryMixin, AOIRelationMixin, RandomPrimaryIdModel):
#    def get_object(self):
#        """Ensures when getting an object, it will be of
#        the same type as it was created, e.g., the type
#        of directory as indicated by its name."""
#        if self.name in SUBCLASSES_OF_DIRECTORY:
#            self.__class__ = SUBCLASSES_OF_DIRECTORY[self.name]
#        return self

    class Meta:
        abstract = True


class HRUZones(Directory):
    xml = models.OneToOneField(XML, related_name="hru_xml")
    hruzones = models.OneToOneField("HRUZonesGDB", related_name="hru_hruGDB")

    @property
    def subdirectory_of(self):
        return self.aoi.directory_path

    def export(self, output_dir):
        outpath = os.path.join(output_dir, self.name)
        os.mkdir(outpath)
        self.xml.export(outpath)
        self.hruzones.export(outpath)


class Maps(Directory):
    maps = GenericRelation(MapDocument, for_concrete_model=False)

    @property
    def subdirectory_of(self):
        return self.aoi.directory_path

    def export(self, output_dir):
        outpath = os.path.join(output_dir, self.name)
        os.mkdir(outpath)
        for mapdoc in self.maps.all():
            mapdoc.export(outpath)


# used for the lookup of geodatabase types with specific models
#SUBCLASSES_OF_DIRECTORY = dict([(cls.__name__, cls)
#                                  for cls in Directory.__subclasses__()])


# *********** GEODATABASE CLASSES ************

class Geodatabase(ProxyMixin, Directory):
    rasters = GenericRelation(Raster, for_concrete_model=False)
    vectors = GenericRelation(Vector, for_concrete_model=False)
    tables = GenericRelation(Table, for_concrete_model=False)

    @property
    def subdirectory_of(self):
        return self.aoi.directory_path

    def export(self, output_dir):
        from arcpy.management import CreateFileGDB
        result = CreateFileGDB(output_dir, self.name)
        outpath = result.getOutput(0)
        for raster in self.rasters.all():
            raster.export(outpath)
        for vector in self.vectors.all():
            vector.export(outpath)
        for table in self.tables.all():
            table.export(outpath)


class Surfaces(Geodatabase):
    class Meta:
        proxy = True


class Layers(Geodatabase):
    def __init__(self, *args, **kwargs):
        # override the default NO_ARCHIVING rule from the
        # Geodatabase class with LAYER_ARCHIVING rule
        self._meta.get_field('archiving_rule').default = LAYER_ARCHIVING
        super(Layers, self).__init__(*args, **kwargs)

    class Meta:
        proxy = True


class AOIdb(Geodatabase):
    class Meta:
        proxy = True


class Prism(Geodatabase):
    def __init__(self, *args, **kwargs):
        # override default NO_ARCHIVING with GROUP_ARCHIVING rule
        self._meta.get_field('archiving_rule').default = GROUP_ARCHIVING
        super(Prism, self).__init__(*args, **kwargs)

    class Meta:
        proxy = True


class Analysis(Geodatabase):
    def __init__(self, *args, **kwargs):
        # override default NO_ARCHIVING with LAYER_ARCHIVING rule
        self._meta.get_field('archiving_rule').default = LAYER_ARCHIVING
        super(Analysis, self).__init__(*args, **kwargs)

    class Meta:
        proxy = True


class HRUZonesGDB(Geodatabase):
    def __init__(self, *args, **kwargs):
        # override default NO_ARCHIVING with LAYER_ARCHIVING rule
        self._meta.get_field('archiving_rule').default = LAYER_ARCHIVING
        super(HRUZones, self).__init__(*args, **kwargs)

    class Meta:
        proxy = True


# used for the lookup of geodatabase types with specific models
SUBCLASSES_OF_GEODATABASE = dict([(cls.__name__, cls)
                                  for cls in Geodatabase.__subclasses__()])


# *************** AOI CLASS ***************

class AOI(CreatedByMixin, DirectoryMixin, RandomPrimaryIdModel):
    shortname = models.CharField(max_length=25)
    boundary = models.MultiPolygonField(srid=GEO_WKID)
    objects = models.GeoManager()
    surfaces = models.OneToOneField(Surfaces, related_name="aoi_surfaces",
                                    null=True, blank=True)
    layers = models.OneToOneField(Layers, related_name="aoi_layers",
                                  null=True, blank=True)
    aoidb = models.OneToOneField(AOIdb, related_name="aoi_aoidb",
                                 null=True, blank=True)
    prism = models.ManyToManyField(Prism, related_name="aoi_prism",
                                   null=True, blank=True)
    analysis = models.OneToOneField(Analysis, related_name="aoi_analysis",
                                    null=True, blank=True)
    maps = models.OneToOneField(Maps, related_name="aoi_maps",
                                null=True, blank=True)
    hruzones = models.ManyToManyField(HRUZones, related_name="aoi_hruzones",
                                      null=True, blank=True)
    subdirectory_of = AOI_DIRECTORY

    class Meta:
        unique_together = ("name",)

    def export(self, output_dir):
        outpath = os.path.join(output_dir, self.name)
        os.mkdir(outpath)

        self.surfaces.export(outpath)
        self.layers.export(outpath)
        self.aoidb.export(outpath)
        self.prism.latest("created_at").export(outpath)
        self.analysis.export(outpath)
        self.maps.export(outpath)

        for hruzone in self.hruzones.all():
            hruzone.export(outpath)


# *************** UPLOAD MODELS ***************
#
#class ChunkedUpload(_ChunkedUpload):
#    __metaclass__ = InheritanceMetaclass
#    type = models.CharField(max_length=25)
#
#    # this will automatically assign the type to the
#    # upload instance to be that of the class
#    # of which it is an instance. In other words,
#    # a n AOIUpload instace will be saved with the type of
#    # AOIUpload.
#    def save(self, *args, **kwargs):
#        if not self.type:
#            self.type = self._meta.model_name
#        super(ChunkedUpload, self).save(*args, **kwargs)
#
#    # this ensures that when getting an object, it will be
#    # of the same type as it was created, e.g., the type of
#    # upload as indicated by its type
#    def get_object(self):
#        if self.type in SUBCLASSES_OF_GEODATABASE:
#            self.__class__ = SUBCLASSES_OF_GEODATABASE[self.type]
#        return self


class AOIUpload(ChunkedUpload):
    task = models.ForeignKey(TaskMeta, related_name='aoi_upload',
                             null=True, blank=True)


class UpdateUpload(ChunkedUpload):
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=10)
    content_object = GenericForeignKey('content_type', 'object_id')
    processed = models.TextField(default="No")


## used for the lookup of geodatabase types with specific models
#SUBCLASSES_OF_UPLOAD = dict([(cls.__name__, cls)
#                             for cls in ChunkedUpload.__subclasses__()])
