from __future__ import absolute_import

from django.conf.urls import url, include
from django.views.generic import TemplateView

from allauth.account import views as allauth_views

from . import views


UUID = r"[a-fA-F0-9]{{8}}-" + \
       r"[a-fA-F0-9]{{4}}-" + \
       r"[a-fA-F0-9]{{4}}-" + \
       r"[a-fA-F0-9]{{4}}-" + \
       r"[a-fA-F0-9]{{12}}"
ID_QUERY = r"(?P<{id}>{uuid})".format(uuid=UUID, id="{id}")
PK_QUERY = ID_QUERY.format(id="pk")


urlpatterns = [
    url(r'^$',
        TemplateView.as_view(template_name='map/map.html'),
        name='ebagis_home'),

    url(r'^aois/$'.format(PK_QUERY),
        TemplateView.as_view(template_name='map/map.html'),
        name='aoi_root_url'),
    url(r'^aois/{}/$'.format(PK_QUERY),
        views.AOIDetailsView.as_view(),
        name='aoi_details'),

    url(r'^about/$',
        TemplateView.as_view(template_name='about.html'),
        name='ebagis_about'),

    url(r'^accounts/login/$', allauth_views.login, name="account_login",
        kwargs={'redirect_authenticated_user': True}),
    url(r'^accounts/profile/$',
        TemplateView.as_view(template_name='userprofile.html'),
        name="account_profile"),

    url(r'^accounts/downloads/$',
        views.DownloadRequestView.as_view(),
        name="account_requests_download"),
    url(r'^accounts/uploads/$',
        views.UploadRequestView.as_view(),
        name="account_requests_upload"),

    url(r'^accounts/', include('allauth.urls')),

]
