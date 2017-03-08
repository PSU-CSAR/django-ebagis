from django.contrib.gis import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.sites import NotRegistered

from .models.aoi import AOI
from .models.geodatabase import Geodatabase
from .models.file import File, Raster
from .models.directory import Maps
from .models.misc import ExpiringToken

from .utils.user import deactivate


admin.site.register(AOI, admin.GeoModelAdmin)
admin.site.register(Geodatabase, admin.ModelAdmin)
admin.site.register(File, admin.ModelAdmin)
admin.site.register(Maps, admin.ModelAdmin)


def gen_new_token(modeladmin, request, queryset):
    for obj in queryset:
        # can be used on both the user admin page
        # and the token admin page, so models vary
        if isinstance(obj, get_user_model()):
            # object is a user model instance
            obj.token.update()
        else:
            # object is a token model instance
            obj.update()
gen_new_token.short_description = \
    "Invalidate and regenerate login token"


class ExpiringTokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created', 'is_valid')
    readonly_fields = list_display
    ordering = ('-created',)
    actions = (gen_new_token, )


admin.site.register(ExpiringToken, ExpiringTokenAdmin)


class ExpiringTokenInline(admin.StackedInline):
    model = ExpiringToken
    can_delete = True
    verbose_name_plural = 'REST auth token'
    readonly_fields = ExpiringTokenAdmin.readonly_fields


def deactivate_user(modeladmin, request, queryset):
    for user in queryset:
        deactivate(user)
deactivate_user.short_description = \
    "Deactivate user and remove all personal info"


class UserAdmin(UserAdmin):
    actions = tuple(UserAdmin.actions) + (
        deactivate_user,
        gen_new_token,
    )
    inlines = (ExpiringTokenInline, )


# Re-register UserAdmin
try:
    admin.site.unregister(get_user_model())
except NotRegistered:
    pass
admin.site.register(get_user_model(), UserAdmin)
