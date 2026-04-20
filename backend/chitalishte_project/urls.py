from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from core import views as core_views

urlpatterns = [
    path("admin/cms/", core_views.legacy_cms_admin_index_redirect),
    re_path(r"^admin/cms/(?P<model_name>[^/]+)/(?P<suffix>.*)$", core_views.legacy_cms_admin_redirect),
    path("admin/", admin.site.urls),
    path("", include("cms.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
