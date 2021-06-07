from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.viewsets import HospitalViewSet, PatientViewSet

router = DefaultRouter()
router.register(r"hospitals", HospitalViewSet)
router.register(r"patients", PatientViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
