from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tmh_registry.users.api.views import ChangePasswordView, SignInView
from tmh_registry.users.api.viewsets import MedicalPersonnelViewSet

router = DefaultRouter()
router.register(r"medical-personnel", MedicalPersonnelViewSet)

urlpatterns = [
    path(r"sign-in/", SignInView.as_view()),
    path(r"", include(router.urls)),
    path(r"change-password/", ChangePasswordView.as_view()),
]
