from __future__ import absolute_import
from django.conf.urls import include, url
from django.contrib.gis import admin

import ebagis.urls
import test_ui.urls

from .settings import REST_ROOT, DEBUG


# admin pages
admin.autodiscover()

# standard django url patterns
urlpatterns = [
    # admin site base url
    url(r'^admin/', include(admin.site.urls)),

    # rest urls
    url(r'^{}'.format(REST_ROOT), include(ebagis.urls.urlpatterns)),

    url(r'^', include(test_ui.urls.urlpatterns)),
]

if DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns