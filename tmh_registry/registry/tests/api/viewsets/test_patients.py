import datetime

from django.test import TestCase
from pytest import mark
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)
from rest_framework.test import APIClient

from .....users.factories import MedicalPersonnelFactory, UserFactory
from ....factories import HospitalFactory, PatientFactory
from ....models import PatientHospitalMapping


@mark.registry
@mark.registry_viewsets
@mark.registry_viewsets_patients
class TestPatientsViewSet(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super(TestPatientsViewSet, cls).setUpClass()

        cls.hospital = HospitalFactory()
        cls.patient = PatientFactory()
        cls.medical_personnel = MedicalPersonnelFactory()
        cls.token = Token.objects.create(user=cls.medical_personnel.user)

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    ######################
    # Test list endpoint #
    ######################

    def test_get_patients_list_successful(self):
        response = self.client.get("/api/v1/patients/", format="json")

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data["count"])
        self.assertEqual(self.patient.id, response.data["results"][0]["id"])
        self.assertEqual([], response.data["results"][0]["hospitals"])
        self.assertNotIn("hospital_id", response.data["results"][0])

    def test_get_patients_list_unauthorized(self):
        self.client = APIClient()
        response = self.client.get("/api/v1/patients/", format="json")

        self.assertEqual(HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_patients_list_from_non_admin_user(self):
        self.non_admin_mp = MedicalPersonnelFactory(user__is_staff=False)
        self.token = Token.objects.create(user=self.non_admin_mp.user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get("/api/v1/patients/", format="json")

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_get_patients_list_from_non_medical_personnel_user(self):
        self.non_mp_user = UserFactory()
        self.token = Token.objects.create(user=self.non_mp_user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get("/api/v1/patients/", format="json")

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    ########################
    # Test detail endpoint #
    ########################

    def test_get_patients_detail_successful(self):
        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/", format="json"
        )

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(self.patient.id, response.data["id"])

    def test_get_patients_detail_unauthorized(self):
        self.client = APIClient()
        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/", format="json"
        )

        self.assertEqual(HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_patients_detail_from_non_admin_user(self):
        self.non_admin_mp = MedicalPersonnelFactory(user__is_staff=False)
        self.token = Token.objects.create(user=self.non_admin_mp.user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/", format="json"
        )

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_get_patients_detail_from_non_medical_personnel_user(self):
        self.non_mp_user = UserFactory()
        self.token = Token.objects.create(user=self.non_mp_user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/", format="json"
        )

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    ########################
    # Test create endpoint #
    ########################

    def test_create_patients_successful(self):
        data = {
            "first_name": "Joan",
            "last_name": "Doe",
            "national_id": 26683571435542132621,
            "age": 23,  # wrong age
            "day_of_birth": 3,
            "month_of_birth": 10,
            "year_of_birth": 1994,
            "gender": "Female",
            "phone_1": 234633241,
            "phone_2": 324362141,
            "address": "16 Test Street, Test City, Test Country",
            "hospital_id": self.hospital.id,
        }
        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_201_CREATED, response.status_code)
        self.assertEqual(data["first_name"], response.data["first_name"])
        self.assertEqual(data["national_id"], response.data["national_id"])
        self.assertEqual(
            datetime.datetime.today().year - data["year_of_birth"],
            response.data["age"],
        )
        self.assertEqual(data["phone_1"], response.data["phone_1"])
        self.assertEqual(data["phone_2"], response.data["phone_2"])

        self.assertEqual(1, len(response.data["hospitals"]))
        self.assertEqual(self.hospital.id, response.data["hospitals"][0]["id"])
        self.assertEqual(
            1,
            PatientHospitalMapping.objects.filter(
                patient_id=response.data["id"], hospital_id=self.hospital.id
            ).count(),
        )

    def test_create_patients_non_medical_personnel_user(self):
        self.non_mp_user = UserFactory()
        self.token = Token.objects.create(user=self.non_mp_user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        data = {
            "first_name": "Joan",
            "last_name": "Doe",
            "national_id": 26683571435542132621,
            "age": 23,  # wrong age
            "day_of_birth": 3,
            "month_of_birth": 10,
            "year_of_birth": 1994,
            "gender": "Female",
            "phone_1": 234633241,
            "phone_2": 324362141,
            "address": "16 Test Street, Test City, Test Country",
            "hospital_id": self.hospital.id,
        }
        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_create_patients_without_year_of_birth_but_with_age(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "national_id": 26683571435542132621,
            "age": 23,
            "day_of_birth": 3,
            "month_of_birth": 10,
            "year_of_birth": None,
            "gender": "Male",
            "phone_1": 234633241,
            "phone_2": 324362141,
            "address": "16 Test Street, Test City, Test Country",
            "hospital_id": self.hospital.id,
        }
        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_201_CREATED, response.status_code)
        self.assertEqual(data["first_name"], response.data["first_name"])
        self.assertEqual(data["national_id"], response.data["national_id"])
        self.assertEqual(data["age"], response.data["age"])
        self.assertEqual(
            datetime.datetime.today().year - data["age"],
            response.data["year_of_birth"],
        )
        self.assertEqual(data["phone_1"], response.data["phone_1"])
        self.assertEqual(data["phone_2"], response.data["phone_2"])
        self.assertEqual(1, len(response.data["hospitals"]))

    def test_create_patients_without_year_of_birth_and_age(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "national_id": 26683571435542132621,
            "age": None,
            "day_of_birth": 3,
            "month_of_birth": 10,
            "year_of_birth": None,
            "gender": "Male",
            "phone_1": 234633241,
            "phone_2": 324362141,
            "address": "16 Test Street, Test City, Test Country",
        }

        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_patient_with_non_existing_hospital_id(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "national_id": 26683571435542132621,
            "age": None,
            "day_of_birth": 3,
            "month_of_birth": 10,
            "year_of_birth": None,
            "gender": "Male",
            "phone_1": 234633241,
            "phone_2": 324362141,
            "address": "16 Test Street, Test City, Test Country",
            "hospital_id": 99999,
        }

        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_patient_without_hospital_id(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "national_id": 26683571435542132621,
            "age": None,
            "day_of_birth": 3,
            "month_of_birth": 10,
            "year_of_birth": None,
            "gender": "Male",
            "phone_1": 234633241,
            "phone_2": 324362141,
            "address": "16 Test Street, Test City, Test Country",
        }

        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)
