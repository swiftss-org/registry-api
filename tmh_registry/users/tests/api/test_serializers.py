from django.test import RequestFactory, TestCase
from mock import MagicMock
from pytest import mark
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_403_FORBIDDEN
from rest_framework.test import APIClient

from tmh_registry.users.api.serializers import UserSerializer
from tmh_registry.users.factories import UserFactory


@mark.users
@mark.users_serializers
class TestUserSerializer(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super(TestUserSerializer, cls).setUpClass()
        cls.request_factory = RequestFactory()

    serializer_class = UserSerializer

    def test_create(self):
        # Prepare users to use in test
        request_user = MagicMock()

        # Prepare payload
        new_email = "test@mail.com"
        create_dict = {
            "email": new_email,
        }

        # Prepare request
        request = self.request_factory.post(
            "/api/v1/users/", content_type="application/json"
        )
        request.user = request_user

        # Perform calls and assertions
        serializer = self.serializer_class(create_dict)
        serializer.context["request"] = request
        result = serializer.create(create_dict)

        self.assertEqual(result.email, new_email)

    def test_create_non_medical_personnel(self):
        self.non_mp_user = UserFactory()
        self.token = Token.objects.create(user=self.non_mp_user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(
            "/api/v1/users/", format="json", data={"email": "new@email.com"}
        )

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_get_me_non_medical_personnel(self):
        self.non_mp_user = UserFactory()
        self.token = Token.objects.create(user=self.non_mp_user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get("/api/v1/users/me/", format="json")

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)
