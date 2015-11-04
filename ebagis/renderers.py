from __future__ import absolute_import

from rest_framework.renderers import JSONRenderer


class GeoJSONRenderer(JSONRenderer):
    format = "geojson"
