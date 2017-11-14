from __future__ import absolute_import

from django.http import Http404


def get_object_owner_or_admin(self):
    lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

    assert lookup_url_kwarg in self.kwargs, (
        'Expected view %s to be called with a URL keyword argument '
        'named "%s". Fix your URL conf, or set the `.lookup_field` '
        'attribute on the view correctly.' %
        (self.__class__.__name__, lookup_url_kwarg)
    )

    query = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

    if not (self.request.user.groups.filter(name='NWCC_ADMIN').exists() or
            self.request.user.is_superuser):
        query['user'] = self.request.user
    try:
        return self.model.objects.get(**query)
    except self.model.DoesNotExist:
        raise Http404


def owner_or_admin(queryset, request,
                   user_field='user', restrict_to_admin=True):
    """
    Filter a queryset. Default is to show only records where user field
    is the current user, unless admin and explicitly requesting all
    matching records. The user field is by default 'user', but that can
    be changed as required.
    """

    user = request.user

    if user.is_anonymous:
        # we don't know who they are, so we give them nothing
        return queryset.none()
    elif ('show_all' in request.query_params and
            (not restrict_to_admin or
             user.groups.filter(name='NWCC_ADMIN').exists() or
             user.is_superuser)):
        # the user wants to see all records,
        # so don't filter by user
        return queryset
    else:
        # normal behavior is to filter by user
        return queryset.filter(**{user_field: user})
