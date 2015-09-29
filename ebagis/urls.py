from __future__ import absolute_import
from django.conf.urls import patterns, include, url
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from . import views


UUID = r"[a-fA-F0-9]{{32}}"
ID_QUERY = r"(?P<{id}>{uuid})".format(uuid=UUID)
PK_QUERY = ID_QUERY.format(id=pk)
AOI_QUERY = ID_QUERY.format(id="aoi_id")
ZONE_QUERY = ID_QUERY.format(id="zones_id")
VERSION_QUERY = ID_QUERY.format(id="version_id")
PROXY_LIST = r"(?P<{base}_type>{proxy_name})"
PROXY_DETAIL = r"{}/{}".format(PROXY_LIST, ID_QUERY)
S = "s"


def pattern_builder(model_name, list_view=None, detail_view=None,
                    download_view=None):
    patterns = []
    if list_view:
        patterns.append(url(r"^$",
                        list_view, name="list"),
    if detail_view:
        patterns.append(url(r"^{}/$".format(PK_QUERY),
                        detail_view, name="detail")
    if download_view:
        patterns.append(url(r"^{}/download/$".format(PK_QUERY),
                        download_view, name="download")
    return (patterns, model_name)


def proxy_pattern_builder(model, list_view=None, detail_view=None,
                          download_view=None):
    model_types = [cls.__name__.lower() for cls in get_subclasses(model, [model])]
    patterns = []
    for type in model_types:
        patterns.append(url(r"^{}/".format(type+S), include(pattern_builder(
            type,
            list_view=list_view,
            detail_view=detail_view,
            download_view=download_view,
        ))))
    return (patterns, model.__name__.lower())


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

file_list = view.FileViewSet.as_view({
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


aoi_patterns=([
    url(r"^$", aoi_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), aoi_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY), aoi_download, name="download"),
], 'aoi')

geodatabase_patterns=([
    url(r"^$", geodatabase_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), geodatabase_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY), geodatabase_download, name="download"),
], 'geodatabase')

zones_patterns=([
    url(r"^$", hruzones_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), hruzones_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY), hruzones_download, name="download"),
], 'hruzones')

prism_patterns=([
    url(r"^$", prism_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), prism_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY), prism_download, name="download"),
], 'prism')

file_patterns=([
    url(r"^$", file_list, name="list"),
    url(r"^{}/$".format(PK_QUERY), file_detail, name="detail"),
    url(r"^{}/download/$".format(PK_QUERY), file_download, name="download"),
], 'file')


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

    # AOI Geodatabases
    url(r"^aois/{}/surfaces/$".format(AOI_QUERY), include(geodatabase_patterns), {"geodatabase_type": "surfaces"}),
    url(r"^aois/{}/surfaces/layers/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "surfaces", 'file_type': 'layer'}),
    url(r"^aois/{}/surfaces/rasters/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "surfaces", 'file_type': 'raster'}),
    url(r"^aois/{}/surfaces/vectors/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "surfaces", 'file_type': 'vector'}),
    url(r"^aois/{}/surfaces/tables/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "surfaces", 'file_type': 'table'}),

    url(r"^aois/{}/layers/$".format(AOI_QUERY), include(geodatabase_patterns), {"geodatabase_type": "layers"}),
    url(r"^aois/{}/layers/layers/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "layers", 'file_type': 'layer'}),
    url(r"^aois/{}/layers/rasters/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "layers", 'file_type': 'raster'}),
    url(r"^aois/{}/layers/vectors/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "layers", 'file_type': 'vector'}),
    url(r"^aois/{}/layers/tables/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "layers", 'file_type': 'table'}),

    url(r"^aois/{}/aoidb/$".format(AOI_QUERY), include(geodatabase_patterns), {"geodatabase_type": "aoidb"}),
    url(r"^aois/{}/aoidb/layers/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "aoidb", 'file_type': 'layer'}),
    url(r"^aois/{}/aoidb/rasters/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "aoidb", 'file_type': 'raster'}),
    url(r"^aois/{}/aoidb/vectors/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "aoidb", 'file_type': 'vector'}),
    url(r"^aois/{}/aoidb/tables/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "aoidb", 'file_type': 'table'}),

    url(r"^aois/{}/analysis/$".format(AOI_QUERY), include(geodatabase_patterns), {"geodatabase_type": "analysis"}),
    url(r"^aois/{}/analysis/layers/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "analysis", 'file_type': 'layer'}),
    url(r"^aois/{}/analysis/rasters/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "analysis", 'file_type': 'raster'}),
    url(r"^aois/{}/analysis/vectors/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "analysis", 'file_type': 'vector'}),
    url(r"^aois/{}/analysis/tables/$".format(AOI_QUERY), include(file_patterns), {"geodatabase_type": "analysis", 'file_type': 'table'}),

    url(r"^aois/{}/prism/$".format(AOI_QUERY), include(geodatabase_patterns), {"geodatabase_type": "prismgdb"}),
    url(r"^aois/{}/prism/{}/layers/$".format(AOI_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "prismgdb", 'file_type': 'layer'}),
    url(r"^aois/{}/prism/{}/rasters/$".format(AOI_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "prismgdb", 'file_type': 'raster'}),
    url(r"^aois/{}/prism/{}/vectors/$".format(AOI_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "prismgdb", 'file_type': 'vector'}),
    url(r"^aois/{}/prism/{}/tables/$".format(AOI_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "prismgdb", 'file_type': 'table'}),

    url(r"^aois/{}/zones/$".format(AOI_QUERY), include(zones_patterns)),
    url(r"^aois/{}/zones/{}/{}/param/$".format(AOI_QUERY, ZONE_QUERY, VERSION_QUERY), include(geodatabase_patterns), {"geodatabase_type": "paramgdb"}),
    url(r"^aois/{}/zones/{}/{}/hru/$".format(AOI_QUERY, ZONE_QUERY, VERSION_QUERY), include(geodatabase_patterns), {"geodatabase_type": "hruzonesgdb"}),
    url(r"^aois/{}/zones/{}/{}/xml/$".format(AOI_QUERY, ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"file_type": "xml"}),

    url(r"^aois/{}/zones/{}/{}/param/layers/$".format(AOI_QUERY, ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "paramgdb", 'file_type': 'layer'}),
    url(r"^aois/{}/zones/{}/{}/param/rasters/$".format(AOI_QUERY, ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "paramgdb", 'file_type': 'raster'}),
    url(r"^aois/{}/zones/{}/{}/param/vectors/$".format(AOI_QUERY, ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "paramgdb", 'file_type': 'vector'}),
    url(r"^aois/{}/zones/{}/{}/param/tables/$".format(AOI_QUERY, ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "paramgdb", 'file_type': 'table'}),

    url(r"^aois/{}/zones/{}/{}/hru/layers/$".format(AOI_QUERY, ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "hruzonesgdb", 'file_type': 'layer'}),
    url(r"^aois/{}/zones/{}/{}/hru/rasters/$".format(AOI_QUERY, ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "hruzonesgdb", 'file_type': 'raster'}),
    url(r"^aois/{}/zones/{}/{}/hru/vectors/$".format(AOI_QUERY, ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "hruzonesgdb", 'file_type': 'vector'}),
    url(r"^aois/{}/zones/{}/{}/hru/tables/$".format(AOI_QUERY, ZONE_QUERY, VERSION_QUERY), include(file_patterns), {"geodatabase_type": "hruzonesgdb", 'file_type': 'table'}),

    # other
    url(r"^aois/{}/maps/$".format(AOI_QUERY), include(file_patterns), {"file_type": "map"}),

)
