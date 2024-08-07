"""downtime URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, re_path, include
from django.contrib import admin
from django.views.generic.base import TemplateView
from rest_framework.routers import DefaultRouter
from schedule.views import DowntimeListView
from schedule.viewsets import DowntimeViewSet
from rest_framework.schemas import get_schema_view
from rest_framework import permissions

from downtime.schema import DowntimeSchemaGenerator
import ocs_authentication.auth_profile.urls as authprofile_urls

router = DefaultRouter()
router.register(r'', DowntimeViewSet, 'downtime')

schema_view = get_schema_view(
    permission_classes=[permissions.AllowAny,],
    generator_class=DowntimeSchemaGenerator,
    public=True,
    authentication_classes=[]
    )

urlpatterns = [
    re_path(r'^$', DowntimeListView.as_view(), name='web-downtime-list'),
    re_path(r'^api/', include(router.urls)),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^authprofile/', include(authprofile_urls)),
    path('openapi/', schema_view, name='openapi-schema'),
    path('redoc/', TemplateView.as_view(
        template_name='redoc.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='redoc')]
