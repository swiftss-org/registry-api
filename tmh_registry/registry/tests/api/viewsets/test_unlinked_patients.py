from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APIClient
from tmh_registry.registry.factories import (
    EpisodeFactory,
    HospitalFactory,
    PatientFactory,
    PatientHospitalMappingFactory,
)
from tmh_registry.registry.models import PreferredHospital
from tmh_registry.users.factories import MedicalPersonnelFactory


class TestUnlinkedPatientsGet(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.medical_personnel = MedicalPersonnelFactory()
        cls.hospital = HospitalFactory()
        cls.other_hospital = HospitalFactory()

        PreferredHospital.objects.create(
            medical_personnel=cls.medical_personnel, hospital=cls.hospital
        )

        # Patient 1: Linked to preferred hospital, has episode -> SHOULD NOT BE RETURNED
        cls.patient_1 = PatientFactory()
        cls.mapping_1 = PatientHospitalMappingFactory(
            patient=cls.patient_1, hospital=cls.hospital
        )
        EpisodeFactory(patient_hospital_mapping=cls.mapping_1)

        # Patient 2: Linked to preferred hospital, NO episode -> SHOULD BE RETURNED
        cls.patient_2 = PatientFactory()
        PatientHospitalMappingFactory(
            patient=cls.patient_2, hospital=cls.hospital
        )

        # Patient 3: Linked to other hospital, NO episode -> SHOULD NOT BE RETURNED
        cls.patient_3 = PatientFactory()
        PatientHospitalMappingFactory(
            patient=cls.patient_3, hospital=cls.other_hospital
        )

    def setUp(self) -> None:
        self.token = Token.objects.create(user=self.medical_personnel.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_get_unlinked_patients(self):
        response = self.client.get("/api/v1/unlinked-patients/")
        self.assertEqual(HTTP_200_OK, response.status_code)

        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(str(data[0]["id"]), str(self.patient_2.id))

    def test_get_unlinked_patients_no_preferred_hospital(self):
        medical_personnel = MedicalPersonnelFactory()
        token = Token.objects.create(user=medical_personnel.user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        response = client.get("/api/v1/unlinked-patients/")
        self.assertEqual(HTTP_200_OK, response.status_code)

        data = response.json()
        self.assertEqual(len(data), 0)
