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
from ....factories import (
    EpisodeFactory,
    HospitalFactory,
    PatientFactory,
    PatientHospitalMappingFactory,
)
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
        cls.patient_hospital_mapping = PatientHospitalMapping.objects.create(
            patient=cls.patient, hospital=cls.hospital
        )
        cls.episode = EpisodeFactory(
            patient_hospital_mapping=cls.patient_hospital_mapping
        )
        cls.medical_personnel = MedicalPersonnelFactory()
        cls.token = Token.objects.create(user=cls.medical_personnel.user)

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def get_patient_test_data(self):
        return {
            "full_name": "Joan Doe",
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
            "patient_hospital_id": "1111",
        }

    ######################
    # Test list endpoint #
    ######################

    def test_get_patients_list_successful(self):
        response = self.client.get("/api/v1/patients/", format="json")

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data["count"])
        self.assertEqual(self.patient.id, response.data["results"][0]["id"])
        self.assertNotIn("hospital_id", response.data["results"][0])

        self.assertEqual(
            1, len(response.data["results"][0]["hospital_mappings"])
        )
        self.assertEqual(
            self.mapping.patient_hospital_id,
            response.data["results"][0]["hospital_mappings"][0][
                "patient_hospital_id"
            ],
        )
        self.assertEqual(
            self.hospital.id,
            response.data["results"][0]["hospital_mappings"][0]["hospital_id"],
        )

    def test_get_patients_list_unauthorized(self):
        self.client = APIClient()
        response = self.client.get("/api/v1/patients/", format="json")

        self.assertEqual(HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_patients_list_from_non_admin_user(self):
        non_admin_mp = MedicalPersonnelFactory(user__is_staff=False)
        non_admin_token = Token.objects.create(user=non_admin_mp.user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + non_admin_token.key)
        response = client.get("/api/v1/patients/", format="json")

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_get_patients_list_from_non_medical_personnel_user(self):
        non_mp_user = UserFactory()
        non_mp_token = Token.objects.create(user=non_mp_user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + non_mp_token.key)
        response = client.get("/api/v1/patients/", format="json")

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
        self.assertEqual(1, len(response.data["hospital_mappings"]))

        patient_hospital_id = PatientHospitalMapping.objects.get(
            hospital=self.hospital.id, patient=self.patient.id
        ).patient_hospital_id

        self.assertEqual(
            self.hospital.id,
            response.data["hospital_mappings"][0]["hospital_id"],
        )
        self.assertEqual(
            patient_hospital_id,
            response.data["hospital_mappings"][0]["patient_hospital_id"],
        )

    def test_get_patients_detail__with_episode_successful(self):
        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/", format="json"
        )

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(self.patient.id, response.data["id"])
        self.assertEqual(True, response.data["episodes"][0]["diathermy_used"])

    def test_get_patients_detail_unauthorized(self):
        self.client = APIClient()
        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/", format="json"
        )

        self.assertEqual(HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_patients_detail_from_non_admin_user(self):
        non_admin_mp = MedicalPersonnelFactory(user__is_staff=False)
        non_admin_token = Token.objects.create(user=non_admin_mp.user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + non_admin_token.key)
        response = client.get(
            f"/api/v1/patients/{self.patient.id}/", format="json"
        )

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_get_patients_detail_from_non_medical_personnel_user(self):
        non_mp_user = UserFactory()
        non_mp_token = Token.objects.create(user=non_mp_user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + non_mp_token.key)
        response = client.get(
            f"/api/v1/patients/{self.patient.id}/", format="json"
        )

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_get_patients_detail_with_multiple_hospitals(self):
        PatientHospitalMappingFactory(patient=self.patient)

        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/", format="json"
        )

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(self.patient.id, response.data["id"])
        self.assertEqual(2, len(response.data["hospital_mappings"]))

        for hospital_mapping in response.data["hospital_mappings"]:
            patient_hospital_id = PatientHospitalMapping.objects.get(
                hospital_id=hospital_mapping["hospital_id"],
                patient_id=self.patient.id,
            ).patient_hospital_id
            self.assertEqual(
                patient_hospital_id, hospital_mapping["patient_hospital_id"]
            )

    ########################
    # Test create endpoint #
    ########################

    def test_create_patients_successful(self):
        data = self.get_patient_test_data()
        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_201_CREATED, response.status_code)
        self.assertEqual(data["full_name"], response.data["full_name"])
        self.assertEqual(data["national_id"], response.data["national_id"])
        self.assertEqual(
            datetime.datetime.today().year - data["year_of_birth"],
            response.data["age"],
        )
        self.assertEqual(data["phone_1"], response.data["phone_1"])
        self.assertEqual(data["phone_2"], response.data["phone_2"])

        self.assertEqual(1, len(response.data["hospital_mappings"]))
        self.assertEqual(
            self.hospital.id,
            response.data["hospital_mappings"][0]["hospital_id"],
        )
        self.assertEqual(
            data["patient_hospital_id"],
            response.data["hospital_mappings"][0]["patient_hospital_id"],
        )
        self.assertEqual(
            1,
            PatientHospitalMapping.objects.filter(
                patient_id=response.data["id"], hospital_id=self.hospital.id
            ).count(),
        )

    def test_create_patients_only_with_mandatory_fields(self):
        data = self.get_patient_test_data()
        for key in data.keys():
            data[key] = None
        data["full_name"] = "John Doe"
        data["year_of_birth"] = 1989
        data["hospital_id"] = self.hospital.id
        data["patient_hospital_id"] = "1111"

        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_201_CREATED, response.status_code)
        self.assertEqual(data["full_name"], response.data["full_name"])
        self.assertEqual(data["year_of_birth"], response.data["year_of_birth"])
        self.assertEqual(
            datetime.datetime.today().year - data["year_of_birth"],
            response.data["age"],
        )

    def test_create_patients_with_already_existing_patient_hospital_id(self):
        data = self.get_patient_test_data()
        PatientHospitalMappingFactory(
            patient_hospital_id=data["patient_hospital_id"],
            hospital_id=data["hospital_id"],
        )

        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_patients_non_medical_personnel_user(self):
        self.non_mp_user = UserFactory()
        self.token = Token.objects.create(user=self.non_mp_user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        data = self.get_patient_test_data()
        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_create_patients_without_year_of_birth_but_with_age(self):
        data = self.get_patient_test_data()
        data["age"] = 23
        data["year_of_birth"] = None
        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_201_CREATED, response.status_code)
        self.assertEqual(data["full_name"], response.data["full_name"])
        self.assertEqual(data["national_id"], response.data["national_id"])
        self.assertEqual(data["age"], response.data["age"])
        self.assertEqual(
            datetime.datetime.today().year - data["age"],
            response.data["year_of_birth"],
        )
        self.assertEqual(data["phone_1"], response.data["phone_1"])
        self.assertEqual(data["phone_2"], response.data["phone_2"])
        self.assertEqual(1, len(response.data["hospital_mappings"]))

    def test_create_patients_without_year_of_birth_and_age(self):
        data = self.get_patient_test_data()
        data["age"] = None
        data["year_of_birth"] = None

        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_patient_with_non_existing_hospital_id(self):
        data = self.get_patient_test_data()
        data["hospital_id"] = 99999

        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_patient_without_hospital_id(self):
        data = self.get_patient_test_data()
        data.pop("hospital_id")

        response = self.client.post(
            "/api/v1/patients/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)
