from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.viewsets import HospitalViewSet

router = DefaultRouter()
router.register(r"hospitals", HospitalViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
