from django.contrib.gis import admin
from .models import AOI
from .models import Surfaces, Layers, Prism, AOIdb, HRUZones
from .models import XML, Raster, Vector, Table
from .models import Maps

admin.site.register(AOI, admin.GeoModelAdmin)
admin.site.register(Surfaces, admin.ModelAdmin)
admin.site.register(Layers, admin.ModelAdmin)
admin.site.register(Prism, admin.ModelAdmin)
admin.site.register(AOIdb, admin.ModelAdmin)
admin.site.register(HRUZones, admin.ModelAdmin)
admin.site.register(XML, admin.ModelAdmin)
admin.site.register(Raster, admin.ModelAdmin)
admin.site.register(Vector, admin.ModelAdmin)
admin.site.register(Table, admin.ModelAdmin)
admin.site.register(Maps, admin.ModelAdmin)
