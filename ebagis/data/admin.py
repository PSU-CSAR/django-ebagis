from django.contrib.gis import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.sites import NotRegistered

from .models.aoi import AOI
from .models.geodatabase import Geodatabase
from .models.file import File, Raster
from .models.directory import Maps


admin.site.register(AOI, admin.GeoModelAdmin)
admin.site.register(Geodatabase, admin.ModelAdmin)
admin.site.register(File, admin.ModelAdmin)
admin.site.register(Maps, admin.ModelAdmin)
