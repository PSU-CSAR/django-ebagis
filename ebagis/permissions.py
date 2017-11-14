from rest_framework import permissions


READ_ACTIONS = [
    'list',
    'retrieve'
]
AUTHENTICATED_ACTIONS = READ_ACTIONS + [
    'download'
]
WRITE_ACTIONS = AUTHENTICATED_ACTIONS + [
    'create',
    'update',
    'partial_update',
]
ADMIN_ACTIONS = WRITE_ACTIONS + [
    'destroy',
]


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj, user_field=None):
        if user_field:
            obj_user = getattr(obj, user_field)
        else:
            try:
                obj_user = getattr(obj, 'created_by')
            except AttributeError:
                obj_user = getattr(obj, 'user')

        return request.user == obj_user


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj, user_field=None):
        if not (request.user and request.user.is_authenticated()):
            return False

        if (
            request.user.groups.filter(name='NWCC_ADMIN').exists() or
            request.user.is_superuser
        ):
            return True

        if user_field:
            obj_user = getattr(obj, user_field)
        else:
            try:
                obj_user = getattr(obj, 'created_by')
            except AttributeError:
                obj_user = getattr(obj, 'user')

        return request.user == obj_user


class IsAdminOrNwccReadOnly(permissions.BasePermission):
    '''
    Only allow access to NWCC Users with write perms reserved for admins.
    '''
    def has_permission(self, request, view):
        return (
                # staff user
                (view.action in READ_ACTIONS and
                 request.user and
                 request.user.is_authenticated() and
                 request.user.groups.filter(name='NWCC_STAFF').exists())
            or
                # admin user
                (view.action in ADMIN_ACTIONS and
                 request.user and
                 request.user.is_authenticated() and
                 (request.user.groups.filter(name='NWCC_ADMIN').exists() or
                  request.user.is_superuser))
        )


class IsNwccWrite(permissions.BasePermission):
    '''
    Let anyone from NWCC do anything
    '''

    def has_permission(self, request, view):
        return (request.user and
                request.user.is_authenticated() and
                (request.user.groups.filter(
                     name__in=['NWCC_ADMIN', 'NWCC_STAFF']
                 ).exists() or
                 request.user.is_superuser))


class CheckAdminStaffAuthOrAnon(permissions.BasePermission):
    '''
    Only allow actions suitable with user permission level.
    '''
    def has_permission(self, request, view):
        return (
                # any user
                (view.action in READ_ACTIONS)
            or
                # authenticated user
                (view.action in AUTHENTICATED_ACTIONS and
                 request.user and
                 request.user.is_authenticated())
            or
                # staff user
                (view.action in WRITE_ACTIONS and
                 request.user and
                 request.user.is_authenticated() and
                 request.user.groups.filter(name='NWCC_STAFF').exists())
            or
                # admin user
                (view.action in ADMIN_ACTIONS and
                 request.user and
                 request.user.is_authenticated() and
                 (request.user.groups.filter(name='NWCC_ADMIN').exists() or
                  request.user.is_superuser))
        )
