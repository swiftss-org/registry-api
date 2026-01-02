from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from mock import MagicMock
from pytest import mark
from rest_framework import status
from tmh_registry.users.api.serializers import (
    UserReadSerializer,
    UserSerializer,
)
from tmh_registry.users.api.viewsets import UserViewSet


@mark.users
@mark.users_viewsets
class TestUserViewSet(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super(TestUserViewSet, cls).setUpClass()
        cls.request_factory = RequestFactory()
        request = cls.request_factory.get(
            "/api/v1/users/",
            content_type="application/json",
        )
        cls.view_set = UserViewSet()
        cls.view_set.request = request

    def test_me(self):
        user = MagicMock()

        self.view_set.action = "me"
        self.view_set.kwargs = {}
        request = self.request_factory.get(
            "/api/v1/users/me/",
            content_type="application/json",
        )
        request.user = user
        request.query_params = {}
        request.data = {"test_data": []}

        self.view_set.request = request

        response = self.view_set.me(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_queryset_admin(self):
        self.view_set.request.user = MagicMock()

        queryset = self.view_set.get_queryset()
        ref_queryset = User.objects.all()
        self.assertEqual(len(queryset), len(ref_queryset))

    def test_get_serializer_class_list(self):
        self.view_set.action = "list"
        self.assertEqual(
            self.view_set.get_serializer_class(), UserReadSerializer
        )

    def test_get_serializer_class_partial_update(self):
        self.view_set.action = "partial_update"
        self.assertEqual(self.view_set.get_serializer_class(), UserSerializer)

    def test_get_serializer_class_retrieve(self):
        self.view_set.action = "retrieve"
        self.assertEqual(
            self.view_set.get_serializer_class(),
            UserReadSerializer,
        )

    def test_get_seriliazer_class_me(self):
        self.view_set.action = "me"
        self.assertEqual(
            self.view_set.get_serializer_class(),
            UserReadSerializer,
        )

    def test_get_serializer_class_update(self):
        self.view_set.action = "update"
        self.assertEqual(self.view_set.get_serializer_class(), UserSerializer)

    def test_get_serializer_class_create(self):
        self.view_set.action = "create"
        self.assertEqual(self.view_set.get_serializer_class(), UserSerializer)

    def test_get_serializer_class_destroy(self):
        self.view_set.action = "destroy"
        self.assertEqual(
            self.view_set.get_serializer_class(),
            UserSerializer,
        )
