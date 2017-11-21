from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.db.utils import Error


def create_or_update_nwcc_user_groups():
    '''Create or update the NWCC_ADMIN and NWCC_STAFF user
    groups to ensure they exist and have all the proper
    permissions for ebagis models.'''
    from django.contrib.auth.models import Group, Permission
    from django.db.models import Q
    from django.contrib.contenttypes.models import ContentType

    # we get the content type IDs for all ebagis.data models
    ebagis_content_types = \
        [ct.id for ct in ContentType.objects.filter(app_label='ebagis_data')]

    # we get all the permissions for the ebagis models
    ebagis_permissions = Permission.objects.filter(
        content_type_id__in=ebagis_content_types
    )

    # we create the NWCC ADMIN group if it does not exist yet
    # then we add the all the ebagis model permissions to it
    admin, created = Group.objects.get_or_create(name='NWCC_ADMIN')
    if created:
        admin.save()
    admin.permissions.add(*ebagis_permissions)
    admin.save()

    # we filter the permissions list to only include the add and
    # change permissions, as we only want those for NWCC STAFF
    ebagis_permissions = ebagis_permissions.filter(
        Q(codename__startswith='add') | Q(codename__startswith='change')
    )

    # now we do the same as above for the NWCC STAFF group,
    # but again, the permissions have been filtered
    staff, created = Group.objects.get_or_create(name='NWCC_STAFF')
    if created:
        staff.save()
    staff.permissions.add(*ebagis_permissions)
    staff.save()


class EbagisConfig(AppConfig):
    name = 'ebagis'
    verbose_name = _("eBAGIS")

    def ready(self):
        # every time the app loads, we want to ensure
        # the NWCC group permissions are up-to-date
        # in case any new models were added
        try:
            create_or_update_nwcc_user_groups()
        except Error:
            print ('Warning: DB does not exist, is not initialized, '
                   'or otherwise has errors.')

        import ebagis.signals
