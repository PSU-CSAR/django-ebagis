from __future__ import absolute_import
from django.conf.urls import patterns, include, url
from rest_framework.authtoken.views import obtain_auth_token

from . import views


UUID = r"[a-fA-F0-9]{{32}}"
ID_QUERY = r"(?P<{id}>{uuid})".format(uuid=UUID)
PK_QUERY = ID_QUERY.format(id="pk")
AOI_QUERY = ID_QUERY.format(id="aoi_id")
ZONE_QUERY = ID_QUERY.format(id="zones_id")
PRISM_QUERY = ID_QUERY.format(id="prism_id")
VERSION_QUERY = ID_QUERY.format(id="version_id")
GEODATABASE_QUERY = ID_QUERY.format(id="geodatabase_id")
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

aoi_list = views.AOIViewSet.as_view({
    "get": "list",
    "put": "create",
    "post": "create",
})
aoi_detail = views.AOIViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})
aoi_download = views.AOIViewSet.as_view({
    "get": "download",
})

prism_list = views.PrismViewSet.as_view({
    "get": "prism",
    "post": "create"
})
prism_detail = views.PrismViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})
prism_download = views.PrismViewSet.as_view({
    "get": "download",
})


hruzones_list = views.HRUZonesViewSet.as_view({
    "get": "list",
    "post": "create"
})
hruzones_detail = views.HRUZonesViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})
hruzones_download = views.HRUZonesViewSet.as_view({
    "get": "download",
})

geodatabase_list = views.GeodatabaseViewSet.as_view({
    "get": "list",
    "post": "create"
})
geodatabase_detail = views.GeodatabaseViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})
geodatabase_download = views.GeodatabaseViewSet.as_view({
    "get": "download",
})

file_list = views.FileViewSet.as_view({
    "get": "list",
    "post": "create"
})
file_detail = views.FileViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})
file_download = views.FileViewSet.as_view({
    "get": "download",
})

download_list = views.DownloadViewSet.as_view({
    "get": "list",
})
download_detail = views.DownloadViewSet.as_view({
    "get": "retrieve",
})


file_patterns = ([
    url(r"^$", file_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), file_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY), file_download, name="download"),
], 'file')

file_patterns_no_id = ([
    url(r"^$", file_detail, name="detail"),
    url(r"^download/$", file_download, name="download"),
], 'file')

prism_patterns = ([
    url(r"^$", prism_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), prism_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY), prism_download, name="download"),
    url(r"^{}/{}/layers/$".format(PRISM_QUERY, VERSION_QUERY), include(file_patterns), {'file_type': 'layer'}),
    url(r"^{}/{}/rasters/$".format(PRISM_QUERY, VERSION_QUERY), include(file_patterns), {'file_type': 'raster'}),
    url(r"^{}/{}/vectors/$".format(PRISM_QUERY, VERSION_QUERY), include(file_patterns), {'file_type': 'vector'}),
    url(r"^{}/{}/tables/$".format(PRISM_QUERY, VERSION_QUERY), include(file_patterns), {'file_type': 'table'}),
], 'prism')

prism_patterns_no_id = ([
    url(r"^$".format(PK_QUERY), prism_detail, name="detail"),
    url(r"^{ownload/$".format(PK_QUERY), prism_download, name="download"),
    url(r"^{}/layers/$".format(VERSION_QUERY), include(file_patterns), {'file_type': 'layer'}),
    url(r"^{}/rasters/$".format(VERSION_QUERY), include(file_patterns), {'file_type': 'raster'}),
    url(r"^{}/vectors/$".format(VERSION_QUERY), include(file_patterns), {'file_type': 'vector'}),
    url(r"^{}/tables/$".format(VERSION_QUERY), include(file_patterns), {'file_type': 'table'}),
], 'prism')

geodatabase_patterns = ([
    url(r"^$", geodatabase_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), geodatabase_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY), geodatabase_download, name="download"),
    url(r"^{}/layers/$".format(GEODATABASE_QUERY), include(file_patterns), {'file_type': 'layer'}),
    url(r"^{}/rasters/$".format(GEODATABASE_QUERY), include(file_patterns), {'file_type': 'raster'}),
    url(r"^{}/vectors/$".format(GEODATABASE_QUERY), include(file_patterns), {'file_type': 'vector'}),
    url(r"^{}/tables/$".format(GEODATABASE_QUERY), include(file_patterns), {'file_type': 'table'}),
], 'geodatabase')

geodatabase_patterns_no_id = ([
    url(r"^$", geodatabase_detail, name="detail"),
    url(r"^download/$", geodatabase_download, name="download"),
    url(r"^layers/$", include(file_patterns), {'file_type': 'layer'}),
    url(r"^rasters/$", include(file_patterns), {'file_type': 'raster'}),
    url(r"^vectors/$", include(file_patterns), {'file_type': 'vector'}),
    url(r"^tables/$", include(file_patterns), {'file_type': 'table'}),
], 'geodatabase')

zones_patterns = ([
    url(r"^$", hruzones_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), hruzones_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY), hruzones_download, name="download"),

    url(r"^{}/{}/xml/$".format(ZONE_QUERY, VERSION_QUERY), include(file_patterns_no_id), {"file_type": "xml"}),

    url(r"^{}/{}/param/$".format(ZONE_QUERY, VERSION_QUERY), include(geodatabase_patterns_no_id), {"geodatabase_type": "paramgdb"}),
    url(r"^{}/{}/param/layers/$".format(ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "paramgdb", 'file_type': 'layer'}),
    url(r"^{}/{}/param/rasters/$".format(ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "paramgdb", 'file_type': 'raster'}),
    url(r"^{}/{}/param/vectors/$".format(ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "paramgdb", 'file_type': 'vector'}),
    url(r"^{}/{}/param/tables/$".format(ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "paramgdb", 'file_type': 'table'}),

    url(r"^{}/{}/hru/$".format(ZONE_QUERY, VERSION_QUERY), include(geodatabase_patterns_no_id), {"geodatabase_type": "hruzonesgdb"}),
    url(r"^{}/{}/hru/layers/$".format(ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "hruzonesgdb", 'file_type': 'layer'}),
    url(r"^{}/{}/hru/rasters/$".format(ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "hruzonesgdb", 'file_type': 'raster'}),
    url(r"^{}/{}/hru/vectors/$".format(ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "hruzonesgdb", 'file_type': 'vector'}),
    url(r"^{}/{}/hru/tables/$".format(ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "hruzonesgdb", 'file_type': 'table'}),
], 'hruzones')

zones_patterns_no_id = ([
    url(r"^{".format(PK_QUERY), hruzones_detail, name="detail"),
    url(r"^{ownload/$".format(PK_QUERY), hruzones_download, name="download"),

    url(r"^{}/xml/$".format(VERSION_QUERY), include(file_patterns_no_id), {"file_type": "xml"}),

    url(r"^{}/param/$".format(VERSION_QUERY), include(geodatabase_patterns_no_id), {"geodatabase_type": "paramgdb"}),
    url(r"^{}/param/layers/$".format(VERSION_QUERY), include(file_patterns), {"geodatabase_type": "paramgdb", 'file_type': 'layer'}),
    url(r"^{}/param/rasters/$".format(VERSION_QUERY), include(file_patterns), {"geodatabase_type": "paramgdb", 'file_type': 'raster'}),
    url(r"^{}/param/vectors/$".format(VERSION_QUERY), include(file_patterns), {"geodatabase_type": "paramgdb", 'file_type': 'vector'}),
    url(r"^{}/param/tables/$".format(VERSION_QUERY), include(file_patterns), {"geodatabase_type": "paramgdb", 'file_type': 'table'}),

    url(r"^{}/hru/$".format(VERSION_QUERY), include(geodatabase_patterns_no_id), {"geodatabase_type": "hruzonesgdb"}),
    url(r"^{}/hru/layers/$".format(VERSION_QUERY), include(file_patterns), {"geodatabase_type": "hruzonesgdb", 'file_type': 'layer'}),
    url(r"^{}/hru/rasters/$".format(VERSION_QUERY), include(file_patterns), {"geodatabase_type": "hruzonesgdb", 'file_type': 'raster'}),
    url(r"^{}/hru/vectors/$".format(VERSION_QUERY), include(file_patterns), {"geodatabase_type": "hruzonesgdb", 'file_type': 'vector'}),
    url(r"^{}/hru/tables/$".format(VERSION_QUERY), include(file_patterns), {"geodatabase_type": "hruzonesgdb", 'file_type': 'table'}),
], 'hruzones')

aoi_patterns = ([
    url(r"^$", aoi_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), aoi_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY), aoi_download, name="download"),
    url(r"^{}/surfaces/$".format(AOI_QUERY), include(geodatabase_patterns_no_id), {"geodatabase_type": "surfaces"}),
    url(r"^{}/layers/$".format(AOI_QUERY), include(geodatabase_patterns_no_id), {"geodatabase_type": "layers"}),
    url(r"^{}/aoidb/$".format(AOI_QUERY), include(geodatabase_patterns_no_id), {"geodatabase_type": "aoidb"}),
    url(r"^{}/analysis/$".format(AOI_QUERY), include(geodatabase_patterns_no_id), {"geodatabase_type": "analysis"}),
    url(r"^{}/prism/$".format(AOI_QUERY), include(prism_patterns_no_id)),
    url(r"^{}/zones/$".format(AOI_QUERY), include(zones_patterns_no_id)),
    url(r"^{}/maps/$".format(AOI_QUERY), include(file_patterns), {"file_type": "map"}),
], 'aoi')


urlpatterns = patterns(
    "",
    # API Root
    url(r"^$", views.APIRoot.as_view()),

    # rest framework auth
    url(r"^api-token-auth/$", obtain_auth_token),
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    url(r"^docs/", include("rest_framework_swagger.urls")),

    # user URLs
    url(r"^users/$", user_list, name="user-list"),
    url(r"^users/(?P<pk>[0-9]+)/$", user_detail, name="user-detail"),
    url(r"^validate-token/$", views.validate_token),
    url(r"^groups/$", group_list, name="group-list"),
    url(r"^groups/(?P<pk>[0-9]+)/$", group_detail, name="group-detail"),
    url(r"^permissions/$", permission_list, name="permission-list"),
    url(r"^permissions/(?P<pk>[0-9]+)/$", permission_detail, name="permission-detail"),

    # upload URLs
    url(r"^uploads/$", views.UploadView.as_view(), name="upload-list"),
    url(r"^uploads/{}/$".format(PK_QUERY), views.UploadView.as_view(), name="upload-detail"),

    # download URLs
    url(r"^downloads/$", download_list, name="download-list"),
    url(r"^downloads/{}/$".format(PK_QUERY), download_detail, name="download-detail"),

    # AOI URLs
    url(r"^aois/$", include(aoi_patterns, namespace="aoi-base")),

    # Geodatabase URLs
    url(r"^geodatabases/$", include(geodatabase_patterns, namespace="geodatabase-base")),
    url(r"^surfaces/$", include(geodatabase_patterns), {'geodatabase_type': 'surfaces'}),
    url(r"^layers/$", include(geodatabase_patterns), {'geodatabase_type': 'layers'}),
    url(r"^aoidbs/$", include(geodatabase_patterns), {'geodatabase_type': 'aoidb'}),
    url(r"^analyses/$", include(geodatabase_patterns), {'geodatabase_type': 'analysis'}),
    url(r"^hruzonesgdbs/$", include(geodatabase_patterns), {'geodatabase_type': 'hruzonesgdb'}),
    url(r"^prismgdbs/$", include(geodatabase_patterns), {'geodatabase_type': 'prism'}),
    url(r"^paramgdbs/$", include(geodatabase_patterns), {'geodatabase_type': 'paramgdb'}),

    # HRU URLs
    url(r"^hruzones/$", include(zones_patterns, namespace="hruzones-base")),

    # Prism URLs
    url(r"^prisms/$", include(prism_patterns, namespace="prism-base")),

    # File URLs
    url(r"^files/$", include(file_patterns, namespace="file-base")),
    url(r"^layers/$", include(file_patterns, namespace="layer-base"), {'file_type': 'layer'}),
    url(r"^rasters/$", include(file_patterns, namespace="raster-base"), {'file_type': 'raster'}),
    url(r"^vectors/$", include(file_patterns, namespace="vector-base"), {'file_type': 'vector'}),
    url(r"^tables/$", include(file_patterns, namespace="table-base"), {'file_type': 'table'}),
    url(r"^maps/$", include(file_patterns, namespace="map-base"), {'file_type': 'map'}),
    url(r"^xmls/$", include(file_patterns, namespace="xml-base"), {'file_type': 'xml'}),
)
