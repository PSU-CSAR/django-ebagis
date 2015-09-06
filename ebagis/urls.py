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


user_list = views.UserViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

user_detail = views.UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

group_list = views.GroupViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

group_detail = views.GroupViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

permission_list = views.PermissionViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

permission_detail = views.PermissionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

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
})

aoi_download = views.AOIViewSet.as_view({
    'get': 'download',
})

aoi_surfaces = views.AOIViewSet.as_view({
    'get': 'surfaces'
})

aoi_layers = views.AOIViewSet.as_view({
    'get': 'layers'
})

aoi_aoidb = views.AOIViewSet.as_view({
    'get': 'aoidb'
})

aoi_analysis = views.AOIViewSet.as_view({
    'get': 'analysis'
})


aoi_prism_list = views.AOIViewSet.as_view({
    'get': 'prism',
    'post': 'create'
})
aoi_prism_detail = views.PrismViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})


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

download_list = views.DownloadViewSet.as_view({
    'get': 'list',
})
download_detail = views.DownloadViewSet.as_view({
    'get': 'retrieve',
})


urlpatterns = patterns(
    '',
    # API Root
    #url(r'^', include(router.urls)),
    url(r'^$', views.APIRoot.as_view()),


    # rest framework auth
    url(r'^api-token-auth/$', obtain_auth_token),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^docs/', include('rest_framework_swagger.urls')),


    # user URLs
    url(r'^users/$', user_list, name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', user_detail, name='user-detail'),
    url(r'^validate-token/$', views.validate_token),

    url(r'^groups/$', group_list, name='group-list'),
    url(r'^groups/(?P<pk>[0-9]+)/$', group_detail, name='group-detail'),

    url(r'^permissions/$', permission_list, name='permission-list'),
    url(r'^permissions/(?P<pk>[0-9]+)/$', permission_detail, name='permission-detail'),


    # upload URLs
    url(r'^uploads/$',
        views.UploadView.as_view(),
        name='upload-list'),
    url(r'^uploads/(?P<pk>[^/.]+)/$',
        views.UploadView.as_view(),
        name='upload-detail'),


    # download URLs
    url(r'^downloads/$', download_list, name='download-list'),
    url(r'^downloads/(?P<pk>[^/.]+)/$', download_detail, name='download-detail'),


    # AOI URLs
    url(r'^aois/$', aoi_list, name='aoi-list'),
    url(r'^aois/(?P<pk>[^/.]+)/$', aoi_detail, name='aoi-detail'),
    url(r'^aois/(?P<pk>[^/.]+)/download/$', aoi_download, name='aoi-download'),


    # AOI Geodatabases
    url(r'^aois/(?P<pk>[^/.]+)/surfaces/$', aoi_surfaces, name='aoi-surfaces'),
    url(r'^aois/(?P<pk>[^/.]+)/layers/$', aoi_layers, name='aoi-layers'),
    url(r'^aois/(?P<pk>[^/.]+)/aoidb/$', aoi_aoidb, name='aoi-aoidb'),
    url(r'^aois/(?P<pk>[^/.]+)/analysis/$', aoi_analysis, name='aoi-analysis'),

    url(r'^aois/(?P<pk>[^/.]+)/prism/$', aoi_prism_list, name='aoi-prism-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/prism/(?P<pk>[^/.]+)/$', aoi_prism_detail, name='aoi-prism-detail'),

    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/$', hruzones_list, name='hruzones-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<pk>[^/.]+)/$', hruzones_detail, name='hruzones-detail'),


    # AOI Geodatabase Layers
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/vectors/$', geodatabase_vector_list, name='geodatabase-vector-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/vectors/(?P<pk>[^/.]+)/$', geodatabase_vector_detail, name='geodatabase-vector-detail'),

    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/tables/$', geodatabase_table_list, name='geodatabase-table-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/tables/(?P<pk>[^/.]+)/$', geodatabase_table_detail, name='geodatabase-table-detail'),

    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/xmls/$', geodatabase_xml_list, name='geodatabase-xml-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/xmls/(?P<pk>[^/.]+)/$', geodatabase_xml_detail, name='geodatabase-xml-detail'),

    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/rasters/$', geodatabase_raster_list, name='geodatabase-raster-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/rasters/(?P<pk>[^/.]+)/$', geodatabase_raster_detail, name='geodatabase-raster-detail'),

    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'id>[^/.]+)/vectors/$', geodatabase_vector_list, name='geodatabase-vector-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'id>[^/.]+)/vectors/(?P<pk>[^/.]+)/$', geodatabase_vector_detail, name='geodatabase-vector-detail'),

    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'id>[^/.]+)/tables/$', geodatabase_table_list, name='geodatabase-table-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'id>[^/.]+)/tables/(?P<pk>[^/.]+)/$', geodatabase_table_detail, name='geodatabase-table-detail'),

    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'id>[^/.]+)/xmls/$', geodatabase_xml_list, name='geodatabase-xml-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'id>[^/.]+)/xmls/(?P<pk>[^/.]+)/$', geodatabase_xml_detail, name='geodatabase-xml-detail'),

    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'id>[^/.]+)/rasters/$', geodatabase_raster_list, name='geodatabase-raster-list'),
    url(r'^aois/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'aoi_id>[^/.]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'name__iexact>[a-z]+)/(?P<' + URL_FILTER_QUERY_ARG_PREFIX + 'id>[^/.]+)/rasters/(?P<pk>[^/.]+)/$', geodatabase_raster_detail, name='geodatabase-raster-detail'),

)
