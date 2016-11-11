from __future__ import absolute_import
from django.conf.urls import include, url
from django.contrib.gis import admin

import ebagis.urls
import ebagis_ui.urls

from .settings import REST_ROOT


# admin pages
admin.autodiscover()

# standard django url patterns
urlpatterns = [
    # login/logout
    # I'm not sure what these are for, actually...
    #url(r'^accounts/login/$', 'django.contrib.auth.views.login',
    #    {'template_name': 'admin/login.html'}),
    #url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),

    # admin site base url
    url(r'^admin/', include(admin.site.urls)),

    # rest urls
    url(r'^{}'.format(REST_ROOT), include(ebagis.urls.urlpatterns)),

    url(r'^', include(ebagis_ui.urls.urlpatterns)),
]
