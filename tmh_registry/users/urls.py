from django.urls import path

from tmh_registry.users.api.views import SignInView

urlpatterns = [
    path(r"sign-in/", SignInView.as_view()),
]
