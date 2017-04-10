from rest_framework import permissions


ADMIN_METHODS = ('DELETE', )


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


class IsAdminOrStaffOrAuthenticated(permissions.BasePermission):
    """
    The authenticated request is from a staff member,
    or is a read-only request.
    """

    def has_permission(self, request, view):
        if (
                # authenticated user trying to GET, HEAD, or OPTIONS
                (request.method in permissions.SAFE_METHODS and
                 request.user and
                 request.user.is_authenticated())
            or
                 # admin user trying to DELETE
                 (request.method in ADMIN_METHODS and
                  request.user and
                  request.user.is_superuser)
            or
                 # staff user trying to do anthing else
                 (request.user and
                  request.user.is_authenticated() and
                  request.user.is_staff)
        ):
            return True
        # user not authenticated or trying to do something
        # without sufficient permission
        return False
