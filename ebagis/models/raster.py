from __future__ import absolute_import

from django.contrib.gis.db import models

from .mixins import NameMixin


class PRISMRaster(NameMixin, models.Model):
    raster = models.RasterField(srid=42303)
