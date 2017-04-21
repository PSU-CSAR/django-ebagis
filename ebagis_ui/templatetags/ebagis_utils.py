from django import template
from django.contrib.contenttypes.models import ContentType


register = template.Library()


@register.filter
def dictsort_lower(lst, key_name):
    return sorted(lst, key=lambda item: getattr(item, key_name).lower())


@register.filter
def content_type(obj):
    if not obj:
        return None
    return ContentType.objects.get_for_model(obj).id