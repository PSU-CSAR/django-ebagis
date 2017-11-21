from django.db import models


class NullFalseBooleanField(models.NullBooleanField):
    def get_prep_value(self, value):
        return True if value else None

    def to_python(self, value):
        value = False if value is None or value in ('None',) else value
        super(NullFalseBooleanField, self).to_python(value)
