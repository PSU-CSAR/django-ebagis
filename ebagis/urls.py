from __future__ import absolute_import
from django.conf.urls import patterns, include, url
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from . import views
from .constants import URL_FILTER_QUERY_ARG_PREFIX


## ROUTER FOR REST API ##
router = DefaultRouter()


#router.register(r'aoi', views.AOIViewSet, base_name='aoi')
router.register(r'user', views.UserViewSet, base_name='user')
router.register(r'groups', views.GroupViewSet, base_name='groups')


aoi_list = views.AOIViewSet.as_view({
    'get': 'list',
    'put': 'create',
    'post': 'create',
})

aoi_detail = views.AOIViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
)}

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


urlpatterns = patterns(
    '',
    # rest framework auth
    url(r'^api-token-auth/$', obtain_auth_token),
    url(r'^api-auth/', include('rest_framework.urls',
                                           namespace='rest_framework')),
    url(r'^docs/', include('rest_framework_swagger.urls')),

    # upload URLs
    url(r'^aoiuploads/$',
        views.AOIUploadView.as_view(),
        name='aoiupload-list'),
    url(r'^aoiuploads/(?P<pk>[^/.]+)/$',
        views.AOIUploadView.as_view(),
        name='aoiupload-detail'),

    url(r'^updateuploads/$',
        views.UpdateUploadView.as_view(),
        name='updateupload-list'),
    url(r'^updateuploads/(?P<pk>[^/.]+)/$',
        views.UpdateUploadView.as_view(),
        name='updateupload-detail'),

    # AOI URLs
    url(r'^', include(router.urls)),
    url(r'^aois/$', aoi_list, name='aoi-list'),
    url(r'^aois/(?P<pk>[^/.]+)/$', aoi_detail, name='aoi-detail'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/$', hruzones_list, name='hruzones-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<pk>[^/.]+)/$', hruzones_detail, name='hruzones-detail'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/vectors/$', geodatabase_vector_list, name='geodatabase-vector-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/vectors/(?P<pk>[^/.]+)/$', geodatabase_vector_detail, name='geodatabase-vector-detail'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/tables/$', geodatabase_table_list, name='geodatabase-table-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/tables/(?P<pk>[^/.]+)/$', geodatabase_table_detail, name='geodatabase-table-detail'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/xmls/$', geodatabase_xml_list, name='geodatabase-xml-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/xmls/(?P<pk>[^/.]+)/$', geodatabase_xml_detail, name='geodatabase-xml-detail'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/rasters/$', geodatabase_raster_list, name='geodatabase-raster-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/rasters/(?P<pk>[^/.]+)/$', geodatabase_raster_detail, name='geodatabase-raster-detail'),
)
