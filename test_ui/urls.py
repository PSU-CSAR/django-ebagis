from __future__ import absolute_import
from django.conf.urls import url

from django.views.generic import TemplateView


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='map/map.html')),
]
