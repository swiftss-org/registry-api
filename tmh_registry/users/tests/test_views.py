from abc import ABC

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from mock import patch
from pytest import mark
from rest_framework import status
from rest_framework.exceptions import ValidationError

from tmh_registry.users.api.views import SignInView


class BaseUserManagementTestView(ABC):
    @classmethod
    def setUpClass(cls) -> None:
        super(BaseUserManagementTestView, cls).setUpClass()
        cls.request_factory = RequestFactory()
        cls.username = "username"
        cls.email = "email@email.com"
        cls.password = "password"
        cls.code = "code"

    def test_validation_error(self):
        data = {}
        request = self.request_factory.post(
            self.url, data, content_type="application/json"
        )

        with self.assertRaises(ValidationError):
            self.view.post(request)


@mark.user_management
@mark.user_management_views
@mark.user_managmenet_views_sign_in
class TestSignInView(BaseUserManagementTestView, TestCase):
    view = SignInView()
    url = "/api/v1/sign-in/"

    @patch("tmh_registry.users.api.views." "authenticate")
    def test_authentication_error(self, authenticate):
        data = {
            "username": self.username,
            "password": self.password,
        }
        request = self.request_factory.post(
            self.url, data, content_type="application/json"
        )
        authenticate.return_value = False

        with self.assertRaises(Exception):
            self.view.post(request)
            authenticate.assert_called_once_with(
                username=self.username, password=self.password
            )

    @patch("tmh_registry.users.api.views." "authenticate")
    def test_user_not_found_error(self, authenticate):
        data = {
            "username": self.username,
            "password": self.password,
        }

        request = self.request_factory.post(
            self.url, data, content_type="application/json"
        )
        authenticate.return_value = True

        with self.assertRaises(Exception):
            self.view.post(request)
            authenticate.assert_called_once_with(
                username=self.username, password=self.password
            )

    @patch("tmh_registry.users.api.views." "authenticate")
    def test_sunny_day(self, authenticate):
        user = User.objects.create(
            username=self.username, email=self.email, password=self.password
        )
        data = {
            "username": self.username,
            "password": self.password,
        }
        authenticate.return_value = user
        request = self.request_factory.post(
            self.url, data, content_type="application/json"
        )

        response = self.view.post(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        authenticate.assert_called_once_with(
            username=self.username, password=self.password
        )
