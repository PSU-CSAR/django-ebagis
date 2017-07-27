from __future__ import absolute_import


def owner_or_admin(queryset, request,
                   user_field='user', restrict_to_admin=True):
    """
    Filter a queryset. Default is to show only records where user field
    is the current user, unless admin and explicitly requesting all
    matching records. THe user field is by default 'user', but that can
    be changed as required.
    """

    user = request.user

    if "show_all" in request.query_params and \
            (not restrict_to_admin or user.is_staff or user.is_admin):
        # the user wants to see all records,
        # so don't filter by user
        return queryset
    elif user.is_anonymous:
        # we don't know who they are, so we give them nothing
        return queryset.none()
    else:
        # normal behavior is to filter by user
        return queryset.filter(**{user_field: user})
