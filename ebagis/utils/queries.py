from __future__ import absolute_import


def admin_queryset_filter(queryset, request):
    """
    Get (and filter) Upload queryset.
    By default, user can only continue uploading his/her own uploads.
    """

    if "show_all" in request.query_params and request.user.is_staff:
        # the user is admin and wants to see all records,
        # so don't filter by user
        return queryset
    else:
        # normal behavior is to filter by user
        return queryset.filter(user=request.user)
