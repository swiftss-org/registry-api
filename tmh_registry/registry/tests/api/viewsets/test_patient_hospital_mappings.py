from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.test import APIClient

from tmh_registry.users.factories import MedicalPersonnelFactory

from ....factories import (
    HospitalFactory,
    PatientFactory,
    PatientHospitalMappingFactory,
)


class TestPatientHospitalMappingViewset(TestCase):
    def setUp(self) -> None:
        self.token = Token.objects.create(user=MedicalPersonnelFactory().user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_create_successful(self):
        patient = PatientFactory()
        hospital = HospitalFactory()
        data = {
            "patient_id": patient.id,
            "hospital_id": hospital.id,
            "patient_hospital_id": "blabla",
        }

        response = self.client.post(
            "/api/v1/patient-hospital-mappings/", data=data, format="json"
        )

        self.assertEqual(HTTP_201_CREATED, response.status_code)
        self.assertEqual(response.data["patient_id"], patient.id)
        self.assertEqual(response.data["hospital_id"], hospital.id)
        self.assertEqual(
            response.data["patient_hospital_id"], data["patient_hospital_id"]
        )

    def test_create_when_mapping_already_exists(self):
        mapping = PatientHospitalMappingFactory()
        data = {
            "patient_id": mapping.patient.id,
            "hospital_id": mapping.hospital.id,
            "patient_hospital_id": mapping.patient_hospital_id,
        }

        response = self.client.post(
            "/api/v1/patient-hospital-mappings/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_when_mapping_already_exists_with_different_patient_hospital_id(
        self,
    ):
        mapping = PatientHospitalMappingFactory()
        data = {
            "patient_id": mapping.patient.id,
            "hospital_id": mapping.hospital.id,
            "patient_hospital_id": "whatever",
        }

        response = self.client.post(
            "/api/v1/patient-hospital-mappings/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_when_patient_hospital_id_already_exists_for_another_patient(
        self,
    ):
        mapping = PatientHospitalMappingFactory()
        patient = PatientFactory()
        data = {
            "patient_id": patient.id,
            "hospital_id": mapping.hospital.id,
            "patient_hospital_id": mapping.patient_hospital_id,
        }

        response = self.client.post(
            "/api/v1/patient-hospital-mappings/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)
