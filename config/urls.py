import os
from django.conf import settings
from django.urls import re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions



# API URLS
api_urls = [
    # API base url
    path("api/v1/", include("config.api_router")),
    path('api-auth/', include('rest_framework.urls')),
]

# ADMIN URLs
admin_urls = [
    path("admin/", admin.site.urls),
]



# Pages URLS

module_type = os.environ.get("DJANGO_SETTINGS_MODULE")
# if the application runs in production mode render home template with some extra info
pages_urls = [
    path(
        "",
        TemplateView.as_view(
            template_name="pages/home.html",
            extra_context={
                "only_token_auth": True
                if "production" in module_type
                else False
            },
        ),
        name="home",
    )
]


# SWAGGER URLS
schema_view = get_schema_view(
    openapi.Info(
        title="TMH Registry",
        default_version="v1",
        description="TMH Registry",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

swagger_urls = [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]


# Static urls
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local
    # web socket development
    static_urls = staticfiles_urlpatterns()
    
else:
    static_urls = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = api_urls + admin_urls + pages_urls + swagger_urls + static_urls

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.

    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
                          path("__debug__/", include(debug_toolbar.urls))
                      ] + urlpatterns
