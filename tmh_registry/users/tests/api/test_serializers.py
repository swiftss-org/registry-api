from django.test import TestCase, RequestFactory
from mock import MagicMock
from tmh_registry.users.api.serializers import UserSerializer
from pytest import mark

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


