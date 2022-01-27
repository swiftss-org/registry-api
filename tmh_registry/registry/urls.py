from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.viewsets import (
    EpisodeViewset,
    HospitalViewSet,
    PatientHospitalMappingViewset,
    PatientViewSet,
)

router = DefaultRouter()
router.register(r"hospitals", HospitalViewSet)
router.register(r"patients", PatientViewSet)
router.register(r"patient-hospital-mappings", PatientHospitalMappingViewset)
router.register(r"episodes", EpisodeViewset)

urlpatterns = [
    path("", include(router.urls)),
]
