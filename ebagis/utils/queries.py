from __future__ import absolute_import

from distutils.util import strtobool


def admin_queryset_filter(queryset, request):
    """
    Get (and filter) Upload queryset.
    By default, user can only continue uploading his/her own uploads.
    """
    show_all = False

    try:
        # use strtobool to accept a variety of strings repr true/false
        show_all = strtobool(request.query_params.get("show_all", "false"))
    except ValueError:
        # the string was not a recognized truth string,
        # so keep show_all as false
        pass

    if show_all and request.user.is_staff:
        # the user is admin and wants to see all records,
        # so don't filter by user
        return queryset
    else:
        # normal behavior is to filter by user
        return queryset.filter(user=request.user)
