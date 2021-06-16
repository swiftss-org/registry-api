from django.test import TestCase
from pytest import mark
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)
from rest_framework.test import APIClient

from .....users.factories import MedicalPersonnelFactory, UserFactory
from ....factories import HospitalFactory


@mark.registry
@mark.registry_viewsets
@mark.registry_viewsets_hospitals
class TestHospitalsViewSet(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super(TestHospitalsViewSet, cls).setUpClass()

        cls.hospital = HospitalFactory()
        cls.medical_personnel = MedicalPersonnelFactory()
        cls.token = Token.objects.create(user=cls.medical_personnel.user)

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    ######################
    # Test list endpoint #
    ######################

    def test_get_hospitals_list_successful(self):
        response = self.client.get("/api/v1/hospitals/", format="json")

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data["count"])
        self.assertEqual(self.hospital.id, response.data["results"][0]["id"])

    def test_get_hospitals_list_unauthorized(self):
        self.client = APIClient()
        response = self.client.get("/api/v1/hospitals/", format="json")

        self.assertEqual(HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_hospitals_list_from_non_admin_user(self):
        self.non_admin_mp = MedicalPersonnelFactory(user__is_staff=False)
        self.token = Token.objects.create(user=self.non_admin_mp.user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get("/api/v1/hospitals/", format="json")

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_get_hospitals_list_from_non_medical_personnel_user(self):
        self.non_mp_user = UserFactory()
        self.token = Token.objects.create(user=self.non_mp_user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get("/api/v1/hospitals/", format="json")

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    ########################
    # Test detail endpoint #
    ########################

    def test_get_hospitals_detail_successful(self):
        response = self.client.get(
            f"/api/v1/hospitals/{self.hospital.id}/", format="json"
        )

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(self.hospital.id, response.data["id"])

    def test_get_hospitals_detail_unauthorized(self):
        self.client = APIClient()
        response = self.client.get(
            f"/api/v1/hospitals/{self.hospital.id}/", format="json"
        )

        self.assertEqual(HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_hospitals_detail_from_non_admin_user(self):
        self.non_admin_mp = MedicalPersonnelFactory(user__is_staff=False)
        self.token = Token.objects.create(user=self.non_admin_mp.user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(
            f"/api/v1/hospitals/{self.hospital.id}/", format="json"
        )

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_get_hospitals_detail_from_non_medical_personnel_user(self):
        self.non_mp_user = UserFactory()
        self.token = Token.objects.create(user=self.non_mp_user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(
            f"/api/v1/hospitals/{self.hospital.id}/", format="json"
        )

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)
