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

from arcpy_extensions.geodatabase import Geodatabase as arcpyGeodatabase
#from arcpy_extensions.layer import Layer as arcpyLayer

from . import constants, utilities

from .settings import AOI_DIRECTORY, GEO_WKID, DOWNLOADS_DIRECTORY,\
                      EXPIRATION_DELTA


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


# *************** FILE CLASSES ***************

class FileData(ProxyMixin, DateMixin, NameMixin, CreatedByMixin,
               AOIRelationMixin, RandomPrimaryIdModel):
    path = models.CharField(max_length=1024, unique=True)
    encoding = models.CharField(max_length=20, null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=10)
    content_object = GenericForeignKey('content_type', 'object_id')

    # TODO Finish this method and those for the sub classes
    # TODO Review all other class create methods -- finish GDB methods
    @classmethod
    @transaction.atomic
    def create(cls, input_file, File, user):
        content_type = ContentType.objects.get_for_model(
            File.__class__,
            for_concrete_model=False
        )

        now = timezone.now()
        name, ext = os.path.splitext(os.path.basename(input_file))
        path = os.path.join(File.content_object.path,
                            name + now.strftime("_%Y%m%d%H%M%S") + ext)
        shutil.copy(input_file, path)

        try:
            data_obj = cls(aoi=File.aoi,
                           content_type=content_type,
                           object_id=File.id,
                           path=path,
                           name=name+ext,
                           created_by=user,
                           created_at=now)
            data_obj.save()
        except:
            try:
                os.remove(path)
            except:
                exception("Failed to remove File Data on create error.")
            raise
        return data_obj

    def export(self, output_dir):
        shutil.copy(self.path, os.path.join(output_dir, self.name))

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


class MapDocumentData(FileData):
    class Meta:
        proxy = True

MapDocumentData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'mapdocument'}


class LayerData(FileData):
    class Meta:
        proxy = True

    @classmethod
    @transaction.atomic
    def create(cls, arcpy_ext_layer, File, user):
        content_type = ContentType.objects.get_for_model(
            File.__class__,
            for_concrete_model=False
        )

        now = timezone.now()
        output_dir = File.content_object.path
        output_name = arcpy_ext_layer.name + now.strftime("_%Y%m%d%H%M%S")
        newlyr = arcpy_ext_layer.copy_to_file(output_dir, outname=output_name)

        print cls

        try:
            data_obj = cls(aoi=File.aoi,
                           content_type=content_type,
                           object_id=File.id,
                           path=newlyr.path,
                           name=arcpy_ext_layer.name,
                           created_by=user,
                           created_at=now)
            data_obj.save()
        except:
            try:
                from arcpy.management import Delete
                Delete(newlyr.path)
            except:
                exception("Failed to remove File Data on create error.")
            raise
        return data_obj


class VectorData(LayerData):
#    srs_wkt = models.CharField(max_length=1000)
#    geom_type = models.CharField(max_length=50)

    class Meta:
        proxy = True

    def export(self, output_dir):
        from arcpy.management import CopyFeatures
        CopyFeatures(self.path, os.path.join(output_dir, self.name))

VectorData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'vector'}


class RasterData(LayerData):
    #srs_wkt = models.CharField(max_length=1000)
    #resolution = models.FloatField()

    class Meta:
        proxy = True

    def export(self, output_dir):
        from arcpy.management import CopyRaster
        CopyRaster(self.path, os.path.join(output_dir, self.name))

RasterData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'raster'}


class TableData(LayerData):
    class Meta:
        proxy = True

    def export(self, output_dir):
        from arcpy.management import CopyRows
        CopyRows(self.path, os.path.join(output_dir, self.name))

TableData._meta.get_field('content_type').limit_choices_to =\
    {"app_label": "ebagis", 'name': 'table'}


# used in the Layer class below to find the proper data class to go
# with a given layer data type
LAYER_DATA_CLASSES = {
    constants.FC_TYPECODE: VectorData,
    constants.RASTER_TYPECODE: RasterData,
    constants.TABLE_TYPECODE: TableData,
}


# ************* LAYER CLASSES **************

class File(ProxyMixin, DateMixin, NameMixin, AOIRelationMixin,
           RandomPrimaryIdModel):
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=10)
    content_object = GenericForeignKey('content_type', 'object_id')
    versions = GenericRelation(FileData, for_concrete_model=False)

    class Meta:
        unique_together = ("content_type", "object_id", "name")

    @classmethod
    @transaction.atomic
    def create(cls, input_file, containing_object, user, data_class=FileData):
        content_type = ContentType.objects.get_for_model(
            containing_object.__class__,
            for_concrete_model=False
        )
        file_name = os.path.splitext(os.path.basename(input_file))[0]
        file_obj = cls(aoi=containing_object.aoi,
                       content_type=content_type,
                       object_id=containing_object.id,
                       name=file_name)
        file_obj.save()
        data_class.create(input_file, file_obj, user)
        return file_obj

    def export(self, output_dir, querydate=timezone.now()):
        super(File, self).export(output_dir, querydate)
        print querydate
        query = self.versions.filter(created_at__lte=querydate)
        print query, len(query)
        return query.latest("created_at").export(output_dir)


class XML(File):
    class Meta:
        proxy = True

    @classmethod
    @transaction.atomic
    def create(cls, input_file, containing_object, user):
        return super(XML, cls).create(input_file,
                                      containing_object,
                                      user,
                                      data_class=XMLData)


class MapDocument(File):
    class Meta:
        proxy = True

    @classmethod
    @transaction.atomic
    def create(cls, input_file, containing_object, user):
        return super(MapDocument, cls).create(input_file,
                                              containing_object,
                                              user,
                                              data_class=MapDocumentData)


class Layer(File):
    class Meta:
        proxy = True

    @classmethod
    @transaction.atomic
    def create(cls, arcpy_ext_layer, geodatabase, user):
        content_type = ContentType.objects.get_for_model(
            geodatabase.__class__,
            for_concrete_model=False
        )
        file_obj = cls(aoi=geodatabase.aoi,
                       content_type=content_type,
                       object_id=geodatabase.id,
                       name=arcpy_ext_layer.name)
        file_obj.save()
        LAYER_DATA_CLASSES[arcpy_ext_layer.type].create(arcpy_ext_layer,
                                                        file_obj,
                                                        user)
        return file_obj


class Vector(Layer):
    class Meta:
        proxy = True


class Raster(Layer):
    class Meta:
        proxy = True


class Table(Layer):
    class Meta:
        proxy = True


# *********** DIRECTORY CLASSES ************

class Directory(DirectoryMixin, AOIRelationMixin, RandomPrimaryIdModel):
    class Meta:
        abstract = True

    @classmethod
    @transaction.atomic
    def create(cls, aoi, name=None):
        if not name:
            name = cls.__name__.lower()
        dir_obj = cls(aoi=aoi, name=name)
        dir_obj.save()
        return dir_obj


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


class Maps(Directory):
    maps = GenericRelation(MapDocument, for_concrete_model=False)

    @property
    def subdirectory_of(self):
        return self.aoi.path

    def export(self, output_dir, querydate=timezone.now()):
        super(Maps, self).export(output_dir, querydate)
        outpath = os.path.join(output_dir, self.name)
        os.mkdir(outpath)
        for mapdoc in self.maps.all():
            mapdoc.export(outpath, querydate=querydate)
        return outpath


# *********** GEODATABASE CLASSES ************

class Geodatabase(ProxyMixin, Directory):
    rasters = GenericRelation(Raster, for_concrete_model=False)
    vectors = GenericRelation(Vector, for_concrete_model=False)
    tables = GenericRelation(Table, for_concrete_model=False)

    @property
    def subdirectory_of(self):
        return self.aoi.path

    @classmethod
    @transaction.atomic
    def create(cls, geodatabase_path, user, aoi):
        gdb_obj = super(Geodatabase, cls).create(aoi)

        # get all geodatabase layers and copy to outdirectory
        gdb = arcpyGeodatabase.Open(geodatabase_path)

        # copy rasters and create raster and raster data objects
        for raster in gdb.rasters:
            Raster.create(raster, gdb_obj, user)

        # copy vectors and create vector and vetor data objects
        for vector in gdb.featureclasses:
            Vector.create(vector, gdb_obj, user)

        # copy tables and create table and table data objects
        for table in gdb.tables:
            Table.create(table, gdb_obj, user)

        return gdb_obj

    def export(self, output_dir, querydate=timezone.now()):
        super(Geodatabase, self).export(output_dir, querydate)
        from arcpy.management import CreateFileGDB
        result = CreateFileGDB(output_dir, self.name)
        outpath = result.getOutput(0)
        for raster in self.rasters.all():
            raster.export(outpath, querydate=querydate)
        for vector in self.vectors.all():
            vector.export(outpath, querydate=querydate)
        for table in self.tables.all():
            table.export(outpath, querydate=querydate)
        return outpath


class Geodatabase_IndividualArchive(Geodatabase):
    def __init__(self, *args, **kwargs):
        # override the default NO_ARCHIVING rule from the
        # directory class with INDIVIDUAL_ARCHIVING rule
        self._meta.get_field('archiving_rule').default = \
            constants.INDIVIDUAL_ARCHIVING
        super(Geodatabase_IndividualArchive, self).__init__(*args, **kwargs)

    class Meta:
        proxy = True


class Geodatabase_GroupArchive(Geodatabase):
    def __init__(self, *args, **kwargs):
        # override default NO_ARCHIVING with GROUP_ARCHIVING rule
        self._meta.get_field('archiving_rule').default = \
            constants.GROUP_ARCHIVING
        super(Geodatabase_GroupArchive, self).__init__(*args, **kwargs)

    class Meta:
        proxy = True


class Geodatabase_ReadOnly(Geodatabase):
    def __init__(self, *args, **kwargs):
        # override default NO_ARCHIVING with READ_ONLY rule
        self._meta.get_field('archiving_rule').default = constants.READ_ONLY
        super(Geodatabase_ReadOnly, self).__init__(*args, **kwargs)

    class Meta:
        proxy = True


class Surfaces(Geodatabase_ReadOnly):
    class Meta:
        proxy = True


class Layers(Geodatabase_IndividualArchive):
    class Meta:
        proxy = True


class AOIdb(Geodatabase_ReadOnly):
    class Meta:
        proxy = True


class Prism(Geodatabase_GroupArchive):
    @property
    def subdirectory_of(self):
        return self.aoi.prism.path

    class Meta:
        proxy = True


class Analysis(Geodatabase_IndividualArchive):
    class Meta:
        proxy = True


class HRUZonesGDB(Geodatabase):
    class Meta:
        proxy = True


class PrismDir(Directory):
    versions = models.ManyToManyField(Prism, related_name="prismdir")

    @property
    def subdirectory_of(self):
        return self.aoi.path

    @classmethod
    @transaction.atomic
    def create(cls, aoi):
        prismdir_obj = super(PrismDir, cls).create(
            aoi, name=constants.PRISM_DIR_NAME
        )

        return prismdir_obj

    def add_prism(self, path, user, aoi):
        self.versions.add(Prism.create(path, user, aoi))

    def export(self, output_dir, querydate=timezone.now()):
        super(PrismDir, self).export(output_dir, querydate)
        filtered = self.versions.filter(created_at__lt=querydate)
        return filtered.latest("created_at").export(output_dir,
                                                    querydate=querydate)


# *************** AOI CLASS ***************

class AOI(CreatedByMixin, DirectoryMixin, RandomPrimaryIdModel):
    shortname = models.CharField(max_length=25)
    boundary = models.MultiPolygonField(srid=GEO_WKID)
    objects = models.GeoManager()

    # data
    surfaces = models.OneToOneField(Surfaces, related_name="aoi_surfaces",
                                    null=True, blank=True)
    layers = models.OneToOneField(Layers, related_name="aoi_layers",
                                  null=True, blank=True)
    aoidb = models.OneToOneField(AOIdb, related_name="aoi_aoidb",
                                 null=True, blank=True)
    prism = models.OneToOneField(PrismDir, related_name="aoi_prism",
                                 null=True, blank=True)
    analysis = models.OneToOneField(Analysis, related_name="aoi_analysis",
                                    null=True, blank=True)
    maps = models.OneToOneField(Maps, related_name="aoi_maps",
                                null=True, blank=True)
    zones = models.OneToOneField(Zones, related_name="aoi_zones",
                                 null=True, blank=True)

    # for making file system changes
    subdirectory_of = AOI_DIRECTORY

    class Meta:
        unique_together = ("name",)

    @classmethod
    @transaction.atomic
    def create(cls, aoi_name, aoi_shortname, user, temp_aoi_path):
        # get multipolygon WKT from AOI Boundary Layer
        wkt, crs_wkt = utilities.get_multipart_wkt_geometry(
            os.path.join(temp_aoi_path, constants.AOI_GDB),
            layername=constants.AOI_BOUNDARY_LAYER
        )

        crs = utilities.create_spatial_ref_from_wkt(crs_wkt)

        if utilities.get_authority_code_from_spatial_ref(crs) != GEO_WKID:
            dst_crs = utilities.create_spatial_ref_from_EPSG(GEO_WKID)
            wkt = utilities.reproject_wkt(wkt, crs, dst_crs)

        aoi = cls(name=aoi_name,
                  shortname=aoi_shortname,
                  boundary=wkt,
                  created_by=user)
        try:
            aoi.save()

            # TODO: convert GDB imports to use celery group or multiprocessing
            # import aoi.gdb
            aoi.aoidb = AOIdb.create(
                os.path.join(temp_aoi_path,
                             constants.AOI_GDB),
                user,
                aoi,
            )

            aoi.save()

            # import surfaces.gdb
            aoi.surfaces = Surfaces.create(
                os.path.join(temp_aoi_path,
                             constants.SURFACES_GDB),
                user,
                aoi,
            )
            aoi.save()

            # import layers.gdb
            aoi.layers = Layers.create(
                os.path.join(temp_aoi_path,
                             constants.LAYERS_GDB),
                user,
                aoi,
            )
            aoi.save()

            # import HRU Zones
            aoi.zones = Zones.create(
                os.path.join(temp_aoi_path,
                             constants.ZONES_DIR_NAME),
                user,
                aoi,
            )

            # import analysis.gdb
            aoi.analysis = Analysis.create(
                os.path.join(temp_aoi_path,
                             constants.ANALYSIS_GDB),
                user,
                aoi,
            )
            aoi.save()

            # import prism.gdb -- need to add dir first, then add prism to it
            aoi.prism = PrismDir.create(
                aoi,
            )
            aoi.save()
            aoi.prism.add_prism(
                os.path.join(temp_aoi_path,
                             constants.PRISM_GDB),
                user,
                aoi,
            )

            # import param.gdb

            # import loose files in param/

            # import param/paramdata.gdb

            # import map docs in maps directory
            aoi.maps = Maps.create(aoi=aoi, name=constants.MAPS_DIR_NAME)
            aoi.save()

        except:
            try:
                if aoi.path:
                    shutil.rmtree(aoi.path)
            except:
                exception("Failed to remove AOI directory on import error.")
            raise

        return aoi

    def export(self, output_dir, querydate=timezone.now(), outname=None):
        super(AOI, self).export(output_dir, querydate)

        # if no outname provided, use the AOI name
        # as the name of the output AOI directory
        if not outname:
            outname = self.name

        # make the AOI directory in the specified loaction
        outpath = os.path.join(output_dir, outname)
        os.mkdir(outpath)

        # make the metadata file for versioning
        # TODO

        # export each part of the AOI
        self.surfaces.export(outpath, querydate=querydate)
        self.layers.export(outpath, querydate=querydate)
        self.aoidb.export(outpath, querydate=querydate)
        self.prism.export(outpath, querydate=querydate)
        self.analysis.export(outpath, querydate=querydate)
        self.maps.export(outpath, querydate=querydate)
        self.zones.export(outpath, querydate=querydate)

        return outpath


# *************** UPLOAD MODELS ***************

class AOIUpload(ChunkedUpload):
    task = models.ForeignKey(TaskMeta, related_name='aoi_upload',
                             null=True, blank=True)


class UpdateUpload(ChunkedUpload):
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=10)
    content_object = GenericForeignKey('content_type', 'object_id')
    processed = models.TextField(default="No")


# *************** DOWNLOAD MODELS ***************

class Download(DateMixin, RandomPrimaryIdModel):
    user = models.ForeignKey(User,
                             related_name="%(class)s",
                             editable=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=10)
    content_object = GenericForeignKey('content_type', 'object_id')
    task = models.ForeignKey(TaskMeta, related_name='download',
                             null=True, blank=True)
    file = models.FileField(max_length=255, null=True, blank=True)
    # TODO: need a way to pass in a date to this
    querydate = models.DateTimeField(default=timezone.now)

    @property
    def expires_at(self):
        return self.created_at + EXPIRATION_DELTA

    @property
    def expired(self):
        return self.expires_at <= timezone.now()

    def delete(self, remove_file=True, *args, **kwargs):
        super(Download, self).delete(*args, **kwargs)
        if remove_file:
            shutil.rmtree(os.path.join(DOWNLOADS_DIRECTORY,
                                       self.id))
