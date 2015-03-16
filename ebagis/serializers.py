import os
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework.reverse import reverse

from djcelery.models import TaskMeta

from .models import AOI
from .models import Surfaces, Layers, Prism, AOIdb, HRUZones, Analysis,\
    Geodatabase
from .models import XML, Raster, Vector, Table, MapDocument
from .models import AOIUpload, UpdateUpload

from .constants import URL_FILTER_QUERY_ARG_PREFIX

from .utilities import validate_path


MULTIPLE_GDBS = ["hru"]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User


class GroupSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse('user-detail',
                       args=[obj.user_id],
                       request=self.context['request'])

    class Meta:
        model = Group


# *************** FILE SERIALIZERS *****************

class FileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        name_key = URL_FILTER_QUERY_ARG_PREFIX + "name__iexact"

        kwargs = {
            URL_FILTER_QUERY_ARG_PREFIX + "aoi_id": obj.content_object.aoi_id,
            "pk": obj.id,
            name_key: obj.content_object.name.lower(),
        }

        if kwargs[name_key] in MULTIPLE_GDBS:
            kwargs[URL_FILTER_QUERY_ARG_PREFIX + "__object_id"] = obj.object_id

        return reverse('geodatabase-' + type(obj).__name__.lower() + '-detail',
                       kwargs=kwargs,
                       request=self.context['request'])


class XMLSerializer(FileSerializer):
    class Meta:
        model = XML


class VectorSerializer(FileSerializer):
    class Meta:
        model = Vector


class RasterSerializer(FileSerializer):
    class Meta:
        model = Raster


class TableSerializer(FileSerializer):
    class Meta:
        model = Table


class MapDocSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse(obj.content_object.name.lower() + '-' +
                       type(obj).__name__.lower() + '-detail',
                       kwargs={"aoi_pk": obj.content_object.aoi_id,
                               "pk": obj.id},
                       request=self.context['request'])

    class Meta:
        model = MapDocument


# *************** GEODATABASE SERIALIZERS *****************

class GeodatabaseSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    rasters = RasterSerializer(read_only=True, many=True)
    vectors = VectorSerializer(read_only=True, many=True)
    tables = TableSerializer(read_only=True, many=True)
    xmls = XMLSerializer(read_only=True, many=True)

    def get_url(self, obj):
        kwargs = {}
        objtype = type(obj).__name__.lower()
        view_name = "aoi-" + objtype

        if objtype in MULTIPLE_GDBS:
            kwargs["pk"] = obj.id
            kwargs["aoi_pk"] = obj.aoi_id
        else:
            kwargs["pk"] = obj.aoi_id

        return reverse(view_name,
                       kwargs=kwargs,
                       request=self.context['request'])

    class Meta:
        model = Geodatabase


class SurfacesSerializer(GeodatabaseSerializer):
    class Meta:
        model = Surfaces


class LayersSerializer(GeodatabaseSerializer):
    class Meta:
        model = Layers


class PrismSerializer(GeodatabaseSerializer):
    class Meta:
        model = Prism


class AOIdbSerializer(GeodatabaseSerializer):
    class Meta:
        model = AOIdb


class AnalysisSerializer(GeodatabaseSerializer):
    class Meta:
        model = Analysis


class HRUZonesSerializer(GeodatabaseSerializer):
    class Meta:
        model = HRUZones


# *************** AOI SERIALIZERS *****************

class AOIListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AOI
        fields = ('url', 'name', 'created_at', 'created_by')


class AOIGeoListSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = AOI
        geo_field = 'boundary'
        fields = ('url', 'name')


class AOISerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='aoi-detail',
                                               read_only=True)
    created_by = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                     read_only=True)
    surfaces = SurfacesSerializer(read_only=True)
    layers = LayersSerializer(read_only=True)
    aoidb = AOIdbSerializer(read_only=True)
    analysis = AnalysisSerializer(read_only=True)
    prism = PrismSerializer(read_only=True)
    #maps = MapDocSerializer(read_only=True, many=True)
    #hruzones = HRUZonesSerializer(read_only=True, many=True)

    class Meta:
        model = AOI
        fields = ("url", "name", "created_by", "created_at", "removed_at",
                  "surfaces", "layers", "aoidb", "analysis", "prism", #"maps",
                  #"hruzones",
        )


class AOIGeoSerializer(GeoFeatureModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='aoi-detail',
                                               read_only=True)
    created_by = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                     read_only=True)
    surfaces = SurfacesSerializer(read_only=True)
    layers = LayersSerializer(read_only=True)
    aoidb = AOIdbSerializer(read_only=True)
    analysis = AnalysisSerializer(read_only=True)
    prism = PrismSerializer(read_only=True)
    #maps = MapDocSerializer(read_only=True, many=True)
    #hruzones = HRUZonesSerializer(read_only=True, many=True)

    class Meta:
        model = AOI
        geo_field = 'boundary'


# *************** UPLOAD SERIALIZERS *****************

class AOITaskSerializer(serializers.ModelSerializer):
    result = serializers.HyperlinkedRelatedField(view_name='aoi-detail',
                                                 read_only=True)

    class Meta:
        model = TaskMeta


class AOIUploadSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="aoiupload-detail")
    user = serializers.HyperlinkedRelatedField(view_name="user-detail",
                                               read_only=True)
    task = AOITaskSerializer(read_only=True)

    def validate_filename(self, value):
        aoi_name = os.path.splitext(value)[0]
        validate_path(aoi_name, allow_whitespace=True)

        try:
            AOI.objects.get(name=aoi_name)
        except AOI.DoesNotExist:
            pass
        else:
            raise Exception("An AOI of the same name already exists.")

        return value

    class Meta:
        model = AOIUpload
        read_only_fields = ('status', 'completed_at', 'task')


class UpdateUploadSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="updateupload-detail")
    user = serializers.HyperlinkedRelatedField(view_name="user-detail",
                                               read_only=True)

    def validate_filename(self, value):
        file_name = os.path.splitext(value)
        validate_path(file_name)
        return value

    class Meta:
        model = UpdateUpload
        read_only_fields = ('status', 'completed_at', 'processed')
