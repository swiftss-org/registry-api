from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.viewsets import (
    DischargeViewset,
    EpisodeViewset,
    FollowUpViewset,
    HospitalViewSet,
    PatientHospitalMappingViewset,
    PatientViewSet,
    PreferredHospitalViewSet,
    SurgeonEpisodeSummaryViewSet,
    OwnedEpisodesViewSet,
)

router = DefaultRouter()
router.register(r"hospitals", HospitalViewSet)
router.register(r"patients", PatientViewSet)
router.register(r"patient-hospital-mappings", PatientHospitalMappingViewset)
router.register(r"episodes", EpisodeViewset)
router.register(r"discharges", DischargeViewset)
router.register(r"follow-ups", FollowUpViewset)
router.register(r"preferred-hospital", PreferredHospitalViewSet, basename='preferred-hospital')
router.register(r'surgeon-episode-summary', SurgeonEpisodeSummaryViewSet, basename='surgeon-episode-summary')
router.register(r"owned-episodes", OwnedEpisodesViewSet, basename='owned-episodes')


urlpatterns = [
    path("", include(router.urls)),
]

# @ todo medical personel required (????)
