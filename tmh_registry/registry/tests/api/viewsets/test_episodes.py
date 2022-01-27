from datetime import date

from django.test import TestCase
from parameterized import parameterized
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.test import APIClient

from tmh_registry.registry.factories import (
    HospitalFactory,
    PatientFactory,
    PatientHospitalMappingFactory,
)
from tmh_registry.registry.models import Episode, PatientHospitalMapping
from tmh_registry.users.factories import MedicalPersonnelFactory


class TestEpisodesViewSet(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super(TestEpisodesViewSet, cls).setUpClass()

        cls.hospital = HospitalFactory()

        cls.patient = PatientFactory(full_name="John Doe")
        cls.patient.created_at = date(year=2021, month=4, day=11)
        cls.patient.save()

        cls.medical_personnel = MedicalPersonnelFactory()
        cls.token = Token.objects.create(user=cls.medical_personnel.user)

    def get_episode_test_data(self):
        return {
            "patient_id": self.patient.id,
            "hospital_id": self.hospital.id,
            "surgery_date": "2021-10-12",
            "episode_type": Episode.EpisodeChoices.UMBILICAL.value,
            "surgeon_ids": [self.medical_personnel.id],
            "comments": "A random comment",
            "cepod": Episode.CepodChoices.PLANNED.value,
            "side": Episode.SideChoices.LEFT.value,
            "occurence": Episode.OccurenceChoices.RECURRENT.value,
            "type": Episode.TypeChoices.INDIRECT.value,
            "complexity": Episode.ComplexityChoices.INCARCERATED.value,
            "mesh_type": Episode.MeshTypeChoices.TNMHP.value,
            "anaesthetic_type": Episode.AnaestheticChoices.SPINAL.value,
            "diathermy_used": True,
        }

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.patient_hospital_mapping = PatientHospitalMappingFactory(
            patient=self.patient, hospital=self.hospital
        )

    def test_create_episode_when_no_patient_hospital_mapping_exists(self):
        PatientHospitalMapping.objects.all().delete()

        data = self.get_episode_test_data()
        response = self.client.post(
            "/api/v1/episodes/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    @parameterized.expand(
        [
            ("episode_type", "hIaTuS"),
            ("cepod", "WRONG_OPTION"),
            ("side", "WRONG_OPTION"),
            ("occurence", "WRONG_OPTION"),
            ("type", "WRONG_OPTION"),
            ("complexity", "WRONG_OPTION"),
            ("mesh_type", "WRONG_OPTION"),
            ("anaesthetic_type", "WRONG_OPTION"),
        ]
    )
    def test_with_non_acceptable_value_for_a_field(self, field, value):
        data = self.get_episode_test_data()
        data[field] = value

        response = self.client.post(
            "/api/v1/episodes/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_episode_successful(self):
        data = self.get_episode_test_data()
        response = self.client.post(
            "/api/v1/episodes/", data=data, format="json"
        )

        self.assertEqual(HTTP_201_CREATED, response.status_code)

        self.assertEqual(
            response.data["patient_hospital_mapping"]["patient_hospital_id"],
            self.patient_hospital_mapping.patient_hospital_id,
        )
        self.assertEqual(response.data["surgery_date"], data["surgery_date"])
        self.assertEqual(response.data["episode_type"], data["episode_type"])

        self.assertEqual(len(response.data["surgeons"]), 1)
        self.assertEqual(
            response.data["surgeons"][0]["user"]["email"],
            self.medical_personnel.user.email,
        )

        self.assertEqual(response.data["comments"], data["comments"])
        self.assertEqual(response.data["cepod"], data["cepod"])
        self.assertEqual(response.data["side"], data["side"])
        self.assertEqual(response.data["occurence"], data["occurence"])
        self.assertEqual(response.data["type"], data["type"])
        self.assertEqual(response.data["complexity"], data["complexity"])
        self.assertEqual(response.data["mesh_type"], data["mesh_type"])
        self.assertEqual(
            response.data["anaesthetic_type"], data["anaesthetic_type"]
        )
        self.assertEqual(
            response.data["diathermy_used"], data["diathermy_used"]
        )
