#from __future__ import absolute_import
from django.conf.urls import patterns, include, url
from django.contrib.gis import admin
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_extensions.routers import ExtendedDefaultRouter

from .settings import REST_ROOT

from ebagisapp import views
from ebagisapp.constants import URL_FILTER_QUERY_ARG_PREFIX


# admin pages
admin.autodiscover()

## ROUTER FOR REST API ##
router = ExtendedDefaultRouter()

# eBagis.shared REST views routes
user_router = router.register(r'user', views.UserViewSet, base_name='user')
user_router.register(r'groups',views.GroupViewSet, base_name='users-group', parents_query_lookups=['user'])

aoi_router = router.register(r'aoi', views.AOIViewSet, base_name='aoi')

hruzones_list = views.HRUZonesViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
hruzones_detail = views.HRUZonesViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

geodatabase_vector_list = views.GeodatabaseVectorViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
geodatabase_vector_detail = views.GeodatabaseVectorViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

geodatabase_table_list = views.GeodatabaseTableViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
geodatabase_table_detail = views.GeodatabaseTableViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

geodatabase_xml_list = views.GeodatabaseXMLViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
geodatabase_xml_detail = views.GeodatabaseXMLViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

geodatabase_raster_list = views.GeodatabaseRasterViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
geodatabase_raster_detail = views.GeodatabaseRasterViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

#layers_router = aoi_router.register(r'layers', shared.views.LayersViewSet, base_name='aoi-layers', parents_query_lookups=['aoi'])
#layers_router.register(r'vector', shared.views.LayersVectorViewSet, base_name='aoi-layers-vector', parents_query_lookups=['aoi', 'object_id'])
#layers_router.register(r'raster', shared.views.LayersRasterViewSet, base_name='aoi-layers-raster', parents_query_lookups=['aoi', 'object_id'])
#layers_router.register(r'table', shared.views.LayersTableViewSet, base_name='aoi-layers-table', parents_query_lookups=['aoi', 'object_id'])
#
#surfaces_router = aoi_router.register(r'surfaces', shared.views.SurfacesViewSet, base_name='aoi-surfaces', parents_query_lookups=['aoi'])
#surfaces_router.register(r'vector', shared.views.SurfacesVectorViewSet, base_name='aoi-surfaces-vector', parents_query_lookups=['aoi', 'object_id'])
#surfaces_router.register(r'raster', shared.views.SurfacesRasterViewSet, base_name='aoi-surfaces-raster', parents_query_lookups=['aoi', 'object_id'])
#surfaces_router.register(r'table', shared.views.SurfacesTableViewSet, base_name='aoi-surfaces-table', parents_query_lookups=['aoi', 'object_id'])
#
#aoidb_router = aoi_router.register(r'aoilayers', shared.views.AOIdbViewSet, base_name='aoi-aoidb', parents_query_lookups=['aoi'])
#aoidb_router.register(r'vector', shared.views.AOIdbVectorViewSet, base_name='aoi-aoidb-vector', parents_query_lookups=['aoi', 'object_id'])
#aoidb_router.register(r'raster', shared.views.AOIdbRasterViewSet, base_name='aoi-aoidb-raster', parents_query_lookups=['aoi', 'object_id'])
#aoidb_router.register(r'table', shared.views.AOIdbTableViewSet, base_name='aoi-aoidb-table', parents_query_lookups=['aoi', 'object_id'])
#
#analysis_router = aoi_router.register(r'analysis', shared.views.AnalysisViewSet, base_name='aoi-analysis', parents_query_lookups=['aoi'])
#analysis_router.register(r'vector', shared.views.AnalysisVectorViewSet, base_name='aoi-analysis-vector', parents_query_lookups=['aoi', 'object_id'])
#analysis_router.register(r'raster', shared.views.AnalysisRasterViewSet, base_name='aoi-analysis-raster', parents_query_lookups=['aoi', 'object_id'])
#analysis_router.register(r'table', shared.views.AnalysisTableViewSet, base_name='aoi-analysis-table', parents_query_lookups=['aoi', 'object_id'])
#
#prism_router = aoi_router.register(r'prism', shared.views.PrismViewSet, base_name='aoi-prism', parents_query_lookups=['aoi'])
#prism_router.register(r'vector', shared.views.PrismVectorViewSet, base_name='aoi-prism-vector', parents_query_lookups=['aoi', 'object_id'])
#prism_router.register(r'raster', shared.views.PrismRasterViewSet, base_name='aoi-prism-raster', parents_query_lookups=['aoi', 'object_id'])
#prism_router.register(r'table', shared.views.PrismTableViewSet, base_name='aoi-prism-table', parents_query_lookups=['aoi', 'object_id'])
#
#hru_router = aoi_router.register(r'hru', shared.views.HRUViewSet, base_name='aoi-hru', parents_query_lookups=['aoi'])
#hru_router.register(r'vector', shared.views.HRUVectorViewSet, base_name='aoi-hru-vector', parents_query_lookups=['aoi', 'object_id'])
#hru_router.register(r'raster', shared.views.HRURasterViewSet, base_name='aoi-hru-raster', parents_query_lookups=['aoi', 'object_id'])
#hru_router.register(r'table', shared.views.HRUTableViewSet, base_name='aoi-hru-table', parents_query_lookups=['aoi', 'object_id'])
#hru_router.register(r'xml', shared.views.HRUXMLViewSet, base_name='aoi-hru-xml', parents_query_lookups=['aoi', 'object_id'])
#
#maps_router = aoi_router.register(r'maps', shared.views.MapsViewSet, base_name='aoi-maps', parents_query_lookups=['aoi'])
#maps_router.register(r'mapdoc', shared.views.MapsMapDocViewSet, base_name='aoi-maps-mapdoc', parents_query_lookups=['aoi', 'object_id'])

# eBagis.importer REST views routes
#router.register(r'Upload', importer.views.UploadViewset)
#router.register(r'ChunkedUpload', importer.views.ChunkedUploadViewset)

# standard django url patterns
urlpatterns = patterns(
    '',

    # login/logout
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'admin/login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),

    # admin site base url
    url(r'^admin/', include(admin.site.urls)),

    # urls settings for djangorest
    #url(REST_ROOT + r'$', shared.views.api_root),



    # rest framework auth
    url(REST_ROOT + r'api-token-auth/$', obtain_auth_token),
    url(REST_ROOT + r'api-auth/', include('rest_framework.urls',
                                           namespace='rest_framework')),
    url(REST_ROOT + r'docs/', include('rest_framework_swagger.urls')),
    url(REST_ROOT, include(router.urls)),

    # upload URLs
    url(REST_ROOT + r'aoiuploads/$',
        views.AOIUploadView.as_view(),
        name='aoiupload-list'),
    url(REST_ROOT + r'aoiuploads/(?P<pk>[^/.]+)/$',
        views.AOIUploadView.as_view(),
        name='aoiupload-detail'),

    url(REST_ROOT + r'updateuploads/$',
        views.UpdateUploadView.as_view(),
        name='updateupload-list'),
    url(REST_ROOT + r'updateuploads/(?P<pk>[^/.]+)/$',
        views.UpdateUploadView.as_view(),
        name='updateupload-detail'),

    # AOI URLs
    url(REST_ROOT + r'aoi/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/$', hruzones_list, name='hruzones-list'),
    url(REST_ROOT + r'aoi/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<pk>[^/.]+)/$', hruzones_detail, name='hruzones-detail'),
    url(REST_ROOT + r'aoi/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/vectors/$', geodatabase_vector_list, name='geodatabase-vector-list'),
    url(REST_ROOT + r'aoi/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/vectors/(?P<pk>[^/.]+)/$', geodatabase_vector_detail, name='geodatabase-vector-detail'),
    url(REST_ROOT + r'aoi/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/tables/$', geodatabase_table_list, name='geodatabase-table-list'),
    url(REST_ROOT + r'aoi/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/tables/(?P<pk>[^/.]+)/$', geodatabase_table_detail, name='geodatabase-table-detail'),
    url(REST_ROOT + r'aoi/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/xmls/$', geodatabase_xml_list, name='geodatabase-xml-list'),
    url(REST_ROOT + r'aoi/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/xmls/(?P<pk>[^/.]+)/$', geodatabase_xml_detail, name='geodatabase-xml-detail'),
    url(REST_ROOT + r'aoi/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/rasters/$', geodatabase_raster_list, name='geodatabase-raster-list'),
    url(REST_ROOT + r'aoi/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/rasters/(?P<pk>[^/.]+)/$', geodatabase_raster_detail, name='geodatabase-raster-detail'),
)

#urlpatterns = format_suffix_patterns(urlpatterns)