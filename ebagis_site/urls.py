from __future__ import absolute_import
from django.conf.urls import include, url
from django.contrib.gis import admin

import ebagis.urls

from .settings import REST_ROOT


# admin pages
admin.autodiscover()

# standard django url patterns
urlpatterns = [
    # login/logout
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'admin/login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),

    # admin site base url
    url(r'^admin/', include(admin.site.urls)),

    # rest urls
    url(REST_ROOT, include(ebagis.urls.urlpatterns)),
]
