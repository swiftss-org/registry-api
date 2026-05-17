from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APIClient
from tmh_registry.users.factories import MedicalPersonnelFactory
from .....factories import (
    EpisodeFactory,
    PatientHospitalMappingFactory,
    PatientFactory,
    HospitalFactory
)

class TestEpisodesGetStats(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.medical_personnel = MedicalPersonnelFactory()

        # Create some hospitals
        cls.hospital_1 = HospitalFactory()
        cls.hospital_2 = HospitalFactory()

        # Create patients
        cls.patient_1 = PatientFactory()
        cls.patient_2 = PatientFactory()
        cls.patient_3 = PatientFactory() # Patient without episode

        # Create mappings
        cls.mapping_1 = PatientHospitalMappingFactory(patient=cls.patient_1, hospital=cls.hospital_1)
        cls.mapping_2 = PatientHospitalMappingFactory(patient=cls.patient_2, hospital=cls.hospital_2)
        cls.mapping_3 = PatientHospitalMappingFactory(patient=cls.patient_3, hospital=cls.hospital_1)

        # Create episodes
        cls.episode_1 = EpisodeFactory(patient_hospital_mapping=cls.mapping_1)
        cls.episode_2 = EpisodeFactory(patient_hospital_mapping=cls.mapping_2)
        cls.episode_3 = EpisodeFactory(patient_hospital_mapping=cls.mapping_1)

    def setUp(self) -> None:
        self.token = Token.objects.create(user=self.medical_personnel.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_stats_global(self):
        response = self.client.get("/api/v1/episodes/stats/")
        self.assertEqual(HTTP_200_OK, response.status_code)

        data = response.json()
        self.assertIn("global", data)
        global_stats = data["global"]
        self.assertEqual(global_stats["total_episodes"], 3)
        self.assertEqual(global_stats["patients_without_episode"], 1)

    def test_stats_by_hospital(self):
        response = self.client.get("/api/v1/episodes/stats/?group_by=hospital")
        self.assertEqual(HTTP_200_OK, response.status_code)

        data = response.json()
        self.assertIn("by_hospital", data)
        by_hospital = data["by_hospital"]

        h1_stats = next(h for h in by_hospital if h["hospital_id"] == self.hospital_1.id)
        self.assertEqual(h1_stats["total_episodes"], 2)
        self.assertEqual(h1_stats["patients_without_episode"], 1)

        h2_stats = next(h for h in by_hospital if h["hospital_id"] == self.hospital_2.id)
        self.assertEqual(h2_stats["total_episodes"], 1)
        self.assertEqual(h2_stats["patients_without_episode"], 0)
