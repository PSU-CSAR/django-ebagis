from __future__ import absolute_import
from django.conf.urls import include, url

from rest_framework.documentation import include_docs_urls

from .data import views as data_views
from .data import models as data_models

from . import views
from . import constants


API_TITLE = 'eBAGIS REST API'
API_DESCRIPTION = '...'


UUID = r"[a-fA-F0-9]{{8}}-" + \
       r"[a-fA-F0-9]{{4}}-" + \
       r"[a-fA-F0-9]{{4}}-" + \
       r"[a-fA-F0-9]{{4}}-" + \
       r"[a-fA-F0-9]{{12}}"
ID_QUERY = r"(?P<{id}>{uuid})".format(uuid=UUID, id="{id}")
PK_QUERY = ID_QUERY.format(id="pk")
AOI_QUERY = ID_QUERY.format(id="aoi_id")
PARENT_QUERY = ID_QUERY.format(id="parent_id")
VERSION_QUERY = ID_QUERY.format(id="version_id")
PROXY_LIST = r"(?P<{base}_type>{proxy_name})"
PROXY_DETAIL = r"{}/{}".format(PROXY_LIST, ID_QUERY)
S = "s"


user_list = views.UserViewSet.as_view({
    "get": "list",
    "post": "create",
})
user_detail = views.UserViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

group_list = views.GroupViewSet.as_view({
    "get": "list",
    "post": "create",
})
group_detail = views.GroupViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

permission_list = views.PermissionViewSet.as_view({
    "get": "list",
    "post": "create",
})
permission_detail = views.PermissionViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

aoi_list = data_views.AOIViewSet.as_view({
    "get": "list",
    "put": "create",
    "post": "create",
})
aoi_detail = data_views.AOIViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})
aoi_download = data_views.AOIViewSet.as_view({
    "get": "download",
})

prism_list = data_views.PrismViewSet.as_view({
    "get": "prism",
    "post": "create"
})
prism_detail = data_views.PrismViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})
prism_download = data_views.PrismViewSet.as_view({
    "get": "download",
})

hruzones_list = data_views.HRUZonesViewSet.as_view({
    "get": "list",
    "post": "create"
})
hruzones_detail = data_views.HRUZonesViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})
hruzones_download = data_views.HRUZonesViewSet.as_view({
    "get": "download",
})
hruzonesdata_detail = data_views.HRUZonesDataViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})

geodatabase_list = data_views.GeodatabaseViewSet.as_view({
    "get": "list",
    "post": "create"
})
geodatabase_detail = data_views.GeodatabaseViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})
geodatabase_download = data_views.GeodatabaseViewSet.as_view({
    "get": "download",
})

maps_list = data_views.MapsViewSet.as_view({
    "get": "list",
    "post": "create"
})
maps_detail = data_views.MapsViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})
maps_download = data_views.MapsViewSet.as_view({
    "get": "download",
})

file_list = data_views.FileViewSet.as_view({
    "get": "list",
    "post": "create"
})
file_detail = data_views.FileViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})
file_download = data_views.FileViewSet.as_view({
    "get": "download",
})

download_list = views.DownloadViewSet.as_view({
    "get": "list",
})
download_detail = views.DownloadViewSet.as_view({
    "get": "retrieve",
})

pourpoint_list = data_views.PourPointViewSet.as_view({
    "get": "list",
    "put": "create",
    "post": "create",
})
pourpoint_detail = data_views.PourPointViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})
pourpoint_aois = data_views.PourPointViewSet.as_view({
    "get": "aois",
})

pourpoint_boundary_list = data_views.PourPointBoundaryViewSet.as_view({
    "get": "list",
    "put": "create",
    "post": "create",
})
pourpoint_boundary_detail = data_views.PourPointBoundaryViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})
pourpoint_boundary_aois = data_views.PourPointBoundaryViewSet.as_view({
    "get": "aois",
})

file_patterns = [
    url(r"^$", file_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), file_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY), file_download, name="download"),
]

file_patterns_no_id = [
    url(r"^$", file_detail, name="detail"),
    url(r"^download/$", file_download, name="download"),
]

geodatabase_patterns = [
    url(r"^$", geodatabase_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), geodatabase_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY),
        geodatabase_download,
        name="download"),
    url(r"^{}/layers/".format(PARENT_QUERY),
        include((file_patterns, "file", "layer")),
        {'file_class': data_models.Layer}),
    url(r"^{}/rasters/".format(PARENT_QUERY),
        include((file_patterns, "file", "raster")),
        {'file_class': data_models.Raster}),
    url(r"^{}/vectors/".format(PARENT_QUERY),
        include((file_patterns, "file", "vector")),
        {'file_class': data_models.Vector}),
    url(r"^{}/tables/".format(PARENT_QUERY),
        include((file_patterns, "file", "table")),
        {'file_class': data_models.Table}),
]

geodatabase_patterns_no_id = [
    url(r"^$", geodatabase_detail, name="detail"),
    url(r"^download/$", geodatabase_download, name="download"),
    url(r"^layers/",
        include((file_patterns, "file", "layer")),
        {'file_class': data_models.Layer}),
    url(r"^rasters/",
        include((file_patterns, "file", "raster")),
        {'file_class': data_models.Raster}),
    url(r"^vectors/",
        include((file_patterns, "file", "vector")),
        {'file_class': data_models.Vector}),
    url(r"^tables/",
        include((file_patterns, "file", "table")),
        {'file_class': data_models.Table}),
]

prism_patterns = [
    url(r"^$", prism_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), prism_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY), prism_download, name="download"),
    url(r"^{}/$".format(PK_QUERY),
        include((geodatabase_patterns, "geodatabase", "geodatabase-prism")),
        {'directory_type': data_models.Prism}),
]

prism_patterns_no_id = [
    url(r"^$", prism_detail, name="detail"),
    url(r"^download/$", prism_download, name="download"),
    url(r"^$",
        include((geodatabase_patterns, "geodatabase", "geodatabase-prism")),
        {'directory_type': data_models.Prism}),
]

zones_data_patterns = [
    url(r"^{}/$".format(PK_QUERY),
        hruzonesdata_detail,
        name="detail"),
    url(r"^{}/xml/".format(PARENT_QUERY),
        include((file_patterns_no_id, "file", "hru-xml"))),
    url(r"^{}/param/".format(PARENT_QUERY),
        include((geodatabase_patterns_no_id, "geodatabase", "hru-param")),
        {"directory_type": data_models.ParamGDB}),
    url(r"^{}/hru/".format(PARENT_QUERY),
        include((geodatabase_patterns_no_id, "geodatabase", "hru-hru")),
        {"directory_type": data_models.HRUZonesGDB}),
]

zones_patterns = [
    url(r"^$", hruzones_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), hruzones_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY),
        hruzones_download,
        name="download"),
    url(r"^{}/".format(PARENT_QUERY),
        include((zones_data_patterns, "zones_data", "zones-data"))),
]

maps_patterns = [
    url(r"^$", maps_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), maps_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY),
        maps_download,
        name="download"),
    url(r"^{}/mapdocs/".format(PARENT_QUERY),
        include((file_patterns, "file", "maps-maps"))),
    url(r"^{}/analysis_xml/".format(PARENT_QUERY),
        include((file_patterns_no_id, "file", "maps-analysis_xml"))),
    url(r"^{}/map_parameters_xml/".format(PARENT_QUERY),
        include((file_patterns_no_id, "file", "maps-map_parameters_txt"))),
]

maps_patterns_no_id = [
    url(r"^$", maps_list, name="list"),
    url(r"^download/$",
        maps_download,
        name="download"),
    url(r"^mapdocs/",
        include((file_patterns, "file", "maps-maps")),
        {'literal_filters': {
            'name__endswith': constants.MAP_EXT,
        }}),
    url(r"^analysis_xml/",
        include((file_patterns_no_id, "file", "maps-analysis_xml")),
        {'literal_filters': {
            'name': constants.MAP_ANALYSISXML_FILE,
        }}),
    url(r"^map_parameters_txt/",
        include((file_patterns_no_id, "file", "maps-map_parameters_txt")),
        {'literal_filters': {
            'name': constants.MAP_PARAMTXT_FILE,
        }}),
]

aoi_patterns = [
    url(r"^$", aoi_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), aoi_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY), aoi_download, name="download"),
    url(r"^{}/surfaces/".format(AOI_QUERY),
        include((geodatabase_patterns_no_id, "surfaces", "aoi-surfaces")),
        {"directory_type": data_models.Surfaces}),
    url(r"^{}/layers/".format(AOI_QUERY),
        include((geodatabase_patterns_no_id, "layers", "aoi-layers")),
        {"directory_type": data_models.Layers}),
    url(r"^{}/aoidb/".format(AOI_QUERY),
        include((geodatabase_patterns_no_id, "aoidb", "aoi-aoidb")),
        {"directory_type": data_models.AOIdb}),
    url(r"^{}/analysis/".format(AOI_QUERY),
        include((geodatabase_patterns_no_id, "analysis", "aoi-analysis")),
        {"directory_type": data_models.Analysis}),
    url(r"^{}/prism/".format(AOI_QUERY),
        include((geodatabase_patterns, "prism", "aoi-prism")),
        {"prism": True, "directory_type": data_models.Prism}),
    url(r"^{}/zones/".format(AOI_QUERY),
        include((zones_patterns, "zones", "aoi-zones")),
        {"generation_skip": True}),
    url(r"^{}/maps/".format(AOI_QUERY),
        include((maps_patterns_no_id, "maps", "aoi-map")),
        {'directory_type': data_models.Maps}),
]

pourpoint_patterns = [
    url(r"^$", pourpoint_list, name="list"),
    url(r"^{}/$".format(r"(?P<pk>[0-9]+)"), pourpoint_detail, name="detail"),
    url(r"^{}/aois/$".format(r"(?P<pk>[0-9]+)"), pourpoint_aois, name="aois"),
]

pourpoint_boundary_patterns = [
    url(r"^$", pourpoint_boundary_list, name="list"),
    url(r"^{}/$".format(r"(?P<pk>[0-9]+)"),
        pourpoint_boundary_detail, name="detail"),
    url(r"^{}/aois/$".format(r"(?P<pk>[0-9]+)"),
        pourpoint_boundary_aois, name="aois"),
]


urlpatterns = [
    # rest framework docs
    #url(
    #    r'^docs/',
    #    include_docs_urls(title=API_TITLE, description=API_DESCRIPTION),
    #),

    # API Root
    url(r"^$", views.APIRoot.as_view()),

    # API version test
    url(r"^api-version/$", views.check_api_version),

    # rest framework auth and account urls
    url(r"^token/$", views.ObtainExpiringAuthToken.as_view()),

    url(
        r"^account/login/$",
        views.ObtainExpiringAuthToken.as_view(),
        {"token_field": "key"},
    ),
    url(
        r"^account/logout/$",
        views.delete_auth_token,
    ),
    url(
        r"^account/user/$",
        views.UserDetailsView.as_view(),
    ),

    url(r"^api-auth/",
        include("rest_framework.urls", namespace="rest_framework")),
    # Swagger was upgraded from 0.3.5 to 2.0.4 and it broke; need to fix it
    #url(r"^docs/", include("rest_framework_swagger.urls")),

    # rest_auth urls
#    url(r'^account/', include('rest_auth.urls')),
#    url(r'^account/registration/', include('rest_auth.registration.urls')),
#    url(r'^account/registration/blackhole',
#        user_detail,
#        name='account_email_verification_sent'),

    # user URLs
    url(r"^users/$", user_list, name="user-list"),
    url(r"^users/(?P<pk>[0-9]+)/$", user_detail, name="user-detail"),
    url(r"^validate-token/$", views.validate_token),
    url(r"^groups/$", group_list, name="group-list"),
    url(r"^groups/(?P<pk>[0-9]+)/$", group_detail, name="group-detail"),
    url(r"^permissions/$", permission_list, name="permission-list"),
    url(r"^permissions/(?P<pk>[0-9]+)/$",
        permission_detail,
        name="permission-detail"),

    # desktop stuff
    url(r"^desktop/settings/$", views.get_settings),
    url(r"^desktop/settings/(?P<module>bagis|bagis-p|bagis-h)/$",
        views.get_settings),
    url(r"^desktop/lyr/$", views.get_lyr),

    # upload URLs
    url(r"^uploads/$", views.UploadView.as_view(), name="upload-list"),
    url(r"^uploads/{}/$".format(PK_QUERY),
        views.UploadView.as_view(),
        name="upload-detail"),
    url(r"^uploads/{}/cancel$".format(PK_QUERY),
        views.cancel_upload,
        name="upload-cancel"),

    # download URLs
    url(r"^downloads/$", download_list, name="download-list"),
    url(r"^downloads/{}/$".format(PK_QUERY),
        download_detail,
        name="download-detail"),

    # AOI URLs
    url(r"^aois/", include((aoi_patterns, "aoi", "aoi-base"))),

    # Geodatabase URLs
    url(r"^geodatabases/",
        include((geodatabase_patterns, "geodatabase", "geodatabase-base"))),
    url(r"^surfaces/",
        include((geodatabase_patterns, "geodatabase", "surfaces-base")),
        {'directory_type': data_models.Surfaces}),
    url(r"^layers/",
        include((geodatabase_patterns, "geodatabase", "layers-base")),
        {'directory_type': data_models.Layers}),
    url(r"^aoidbs/",
        include((geodatabase_patterns, "geodatabase", "aoidb-base")),
        {'directory_type': data_models.AOIdb}),
    url(r"^analyses/",
        include((geodatabase_patterns, "geodatabase", "analysis-base")),
        {'directory_type': data_models.Analysis}),
    url(r"^hruzonesgdbs/",
        include((geodatabase_patterns, "geodatabase", "hruzonesgdb-base")),
        {'directory_type': data_models.HRUZonesGDB}),
    url(r"^prisms/",
        include((geodatabase_patterns, "geodatabase", "prism-base")),
        {"prism": True, 'geodatabase_type': data_models.Prism}),
    url(r"^paramgdbs/",
        include((geodatabase_patterns, "geodatabase", "paramgdb-base")),
        {'directory_type': data_models.ParamGDB}),

    # Maps URLs
    url(r"^maps/",
        include((maps_patterns, "maps", "maps-base")),
        {'directory_type': data_models.Maps}),


    # HRU URLs
    url(r"^zones/",
        include((zones_patterns, "zones", "hruzones-base")),
        {"generation_skip": True}),

    url(r"^hruzonesdata/",
        include((zones_data_patterns, "zones_data", "hruzonesdata-base")),
        {"generation_skip": True}),

    # File URLs
    url(r"^files/",
        include((file_patterns, "file", "file-base"))),
    url(r"^layers/",
        include((file_patterns, "file", "layer-base")),
        {'file_class': data_models.Layer}),
    url(r"^rasters/",
        include((file_patterns, "file", "raster-base")),
        {'file_class': data_models.Raster}),
    url(r"^vectors/",
        include((file_patterns, "file", "vector-base")),
        {'file_class': data_models.Vector}),
    url(r"^tables/",
        include((file_patterns, "file", "table-base")),
        {'file_class': data_models.Table}),

    # Pourpoint URLs
    url(r"^pourpoints/", include((
        pourpoint_patterns,
        "pourpoint",
        "pourpoint-base",
    ))),
    url(r"^pourpoint-boundaries/", include((
        pourpoint_boundary_patterns,
        "pourpoint-boundary",
        "pourpoint-boundary-base",
    ))),
]
