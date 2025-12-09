from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.viewsets import (
    AnnouncementViewSet,
    DischargeViewset,
    EpisodeViewset,
    FollowUpViewset,
    HospitalViewSet,
    OwnedEpisodesViewSet,
    PatientHospitalMappingViewset,
    PatientViewSet,
    PreferredHospitalViewSet,
    SurgeonEpisodeSummaryViewSet,
    UnlinkedPatientsViewSet,
)

router = DefaultRouter()
router.register(r"hospitals", HospitalViewSet)
router.register(r"patients", PatientViewSet)
router.register(r"patient-hospital-mappings", PatientHospitalMappingViewset)
router.register(r"episodes", EpisodeViewset)
router.register(r"discharges", DischargeViewset)
router.register(r"follow-ups", FollowUpViewset)
router.register(
    r"preferred-hospital",
    PreferredHospitalViewSet,
    basename="preferred-hospital",
)
router.register(
    r"surgeon-episode-summary",
    SurgeonEpisodeSummaryViewSet,
    basename="surgeon-episode-summary",
)
router.register(
    r"owned-episodes", OwnedEpisodesViewSet, basename="owned-episodes"
)
router.register(
    r"unlinked-patients", UnlinkedPatientsViewSet, basename="unlinked-patients"
)
router.register(
    r"announcements", AnnouncementViewSet, basename="announcements"
)

urlpatterns = [
    path("", include(router.urls)),
]

# @ todo medical personel required (????)
