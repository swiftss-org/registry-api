from datetime import date

from django.test import TestCase
from parameterized import parameterized
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.test import APIClient

from tmh_registry.common.utils.functions import (
    get_text_choice_value_from_label,
)
from tmh_registry.registry.factories import (
    HospitalFactory,
    PatientFactory,
    PatientHospitalMappingFactory,
)
from tmh_registry.registry.models import Episode, PatientHospitalMapping
from tmh_registry.users.factories import MedicalPersonnelFactory


class TestEpisodesPost(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super(TestEpisodesPost, cls).setUpClass()

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
            "episode_type": Episode.EpisodeChoices.UMBILICAL.label,
            "surgeon_ids": [self.medical_personnel.id],
            "comments": "A random comment",
            "cepod": Episode.CepodChoices.PLANNED.label,
            "side": Episode.SideChoices.LEFT.label,
            "occurence": Episode.OccurenceChoices.RECURRENT.label,
            "type": Episode.TypeChoices.INDIRECT.label,
            "size": Episode.SizeChoices.MEDIUM.label,
            "complexity": Episode.ComplexityChoices.INCARCERATED.label,
            "mesh_type": Episode.MeshTypeChoices.TNMHP.label,
            "anaesthetic_type": Episode.AnaestheticChoices.SPINAL.label,
            "diathermy_used": True,
            "antibiotic_used": True,
            "antibiotic_type": 'A random antibiotic',
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
            ("episode_type", "WRONG_OPTION"),
            ("cepod", "WRONG_OPTION"),
            ("side", "WRONG_OPTION"),
            ("occurence", "WRONG_OPTION"),
            ("type", "WRONG_OPTION"),
            ("size", "WRONG_OPTION"),
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
            int(self.patient_hospital_mapping.patient_hospital_id),
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
        self.assertEqual(response.data["size"], data["size"])
        self.assertEqual(response.data["complexity"], data["complexity"])
        self.assertEqual(response.data["mesh_type"], data["mesh_type"])
        self.assertEqual(
            response.data["anaesthetic_type"], data["anaesthetic_type"]
        )
        self.assertEqual(
            response.data["diathermy_used"], data["diathermy_used"]
        )
        self.assertEqual(
            response.data["antibiotic_used"], data["antibiotic_used"]
        )
        self.assertEqual(
            response.data["antibiotic_type"], data["antibiotic_type"]
        )

        # assert that values are stored in the db, not labels
        episode = Episode.objects.get(id=response.data["id"])

        self.assertEqual(
            episode.episode_type,
            get_text_choice_value_from_label(
                Episode.EpisodeChoices.choices, data["episode_type"]
            ),
        )
        self.assertEqual(
            episode.cepod,
            get_text_choice_value_from_label(
                Episode.CepodChoices.choices, data["cepod"]
            ),
        )
        self.assertEqual(
            episode.side,
            get_text_choice_value_from_label(
                Episode.SideChoices.choices, data["side"]
            ),
        )
        self.assertEqual(
            episode.occurence,
            get_text_choice_value_from_label(
                Episode.OccurenceChoices.choices, data["occurence"]
            ),
        )
        self.assertEqual(
            episode.type,
            get_text_choice_value_from_label(
                Episode.TypeChoices.choices, data["type"]
            ),
        )
        self.assertEqual(
            episode.size,
            get_text_choice_value_from_label(
                Episode.SizeChoices.choices, data["size"]
            ),
        )
        self.assertEqual(
            episode.complexity,
            get_text_choice_value_from_label(
                Episode.ComplexityChoices.choices, data["complexity"]
            ),
        )
        self.assertEqual(
            episode.mesh_type,
            get_text_choice_value_from_label(
                Episode.MeshTypeChoices.choices, data["mesh_type"]
            ),
        )
        self.assertEqual(
            episode.anaesthetic_type,
            get_text_choice_value_from_label(
                Episode.AnaestheticChoices.choices, data["anaesthetic_type"]
            ),
        )

    def test_create_successful_without_optional_fields(self):
        data = self.get_episode_test_data()
        data.pop("comments")
        response = self.client.post(
            "/api/v1/episodes/", data=data, format="json"
        )

        self.assertEqual(HTTP_201_CREATED, response.status_code)

        self.assertEqual(response.data["comments"], "")
