from __future__ import absolute_import

import django_filters as filters
from rest_framework import ISO_8601


FilterSet = filters.FilterSet


class CreatedByMixin(FilterSet):
    user_field = "created_by"
    created_by = filters.CharFilter(
        name="{}__username".format(user_field),
        lookup_expr="icontains",
    )

    class Meta:
        abstract = True


class CreatedAtMixin(FilterSet):
    created_at_field = "created_at"
    created_at = filters.IsoDateTimeFilter(
        name=created_at_field,
        input_formats=(ISO_8601, "%m/%d/%Y %H:%M:%S"),
    )
    created_after = filters.IsoDateTimeFilter(
        name=created_at_field,
        lookup_type="gte",
        input_formats=(ISO_8601, "%m/%d/%Y %H:%M:%S"),
    )
    created_before = filters.IsoDateTimeFilter(
        name=created_at_field,
        lookup_type="lte",
        input_formats=(ISO_8601, "%m/%d/%Y %H:%M:%S"),
    )

    class Meta:
        abstract = True


class ModifiedAtMixin(FilterSet):
    modified_at_field = "modified_at"
    modified_at = filters.IsoDateTimeFilter(
        name=modified_at_field,
    )
    modified_after = filters.IsoDateTimeFilter(
        name=modified_at_field,
        lookup_type="gte",
        input_formats=(ISO_8601, "%m/%d/%Y %H:%M:%S"),
    )
    modified_before = filters.IsoDateTimeFilter(
        name=modified_at_field,
        lookup_type="lte",
        input_formats=(ISO_8601, "%m/%d/%Y %H:%M:%S"),
    )

    class Meta:
        abstract = True


class BaseFilterSet(CreatedAtMixin, CreatedByMixin, ModifiedAtMixin,
                    FilterSet):
    class Meta:
        abstract = True


def make_model_filter(model, base=BaseFilterSet, exclude_fields=[]):
    return type(
        "{}Filter".format(model.__class__.__name__),
        (base,),
        {'Meta': type(
            'Meta',
            (object, ),
            {"model": model, "exclude": exclude_fields}
        )},
    )