from __future__ import absolute_import
from django.conf.urls import patterns, include, url
from django.contrib.gis import admin

from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


import ebagis.urls

from .settings import REST_ROOT


# admin pages
admin.autodiscover()

# standard django url patterns
urlpatterns = patterns(
    '',

    # login/logout
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'admin/login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    url(r"^account/", include("account.urls")),

    # admin site base url
    url(r'^admin/', include(admin.site.urls)),

    # rest urls
    url(REST_ROOT, include(ebagis.urls)),
)
