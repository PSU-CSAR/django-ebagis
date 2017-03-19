from __future__ import absolute_import

from django.conf.urls import url, include
from django.views.generic import TemplateView

from allauth.account import views as allauth_views


urlpatterns = [
    url(r'^$',
        TemplateView.as_view(template_name='map/map.html'),
        name='ebagis_home'),
    url(r'^accounts/login/$', allauth_views.login, name="account_login",
        kwargs={'redirect_authenticated_user': True}),
    url(r'^accounts/', include('allauth.urls')),
]
