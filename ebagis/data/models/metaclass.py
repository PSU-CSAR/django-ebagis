from __future__ import absolute_import
from django.db.models.base import ModelBase


class InheritanceMetaclass(ModelBase):
    """Allows a model to return the subclass types from
    the name field. That is, if you want a Surfaces geodatabase,
    where Surfaces is a proxy of the Geodatabase class, you'll
    get a Surfaces instance, not a Geodatabase instance.

    Used with the ProxyMixin."""
    def __call__(cls, *args, **kwargs):
        obj = super(InheritanceMetaclass, cls).__call__(*args, **kwargs)
        return obj.get_object()
