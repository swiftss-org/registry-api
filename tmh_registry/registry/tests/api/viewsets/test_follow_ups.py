from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.test import APIClient

from tmh_registry.common.utils.functions import (
    get_text_choice_value_from_label,
)
from tmh_registry.registry.factories import DischargeFactory, EpisodeFactory
from tmh_registry.registry.models import FollowUp
from tmh_registry.users.factories import MedicalPersonnelFactory


class TestFollowUpsCreate(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super(TestFollowUpsCreate, cls).setUpClass()

        cls.episode = EpisodeFactory(surgery_date="2022-01-23")
        cls.discharge = DischargeFactory(
            episode=cls.episode, date="2022-02-19"
        )

        cls.medical_personnel = MedicalPersonnelFactory()
        cls.token = Token.objects.create(user=cls.medical_personnel.user)

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def get_follow_up_data(self):
        return {
            "episode_id": self.episode.id,
            "date": "2022-02-22",
            "attendee_ids": [self.medical_personnel.id],
            "pain_severity": "Mild",
            "mesh_awareness": False,
            "seroma": True,
            "infection": False,
            "numbness": True,
        }

    def test_successful(self):
        data = self.get_follow_up_data()
        response = self.client.post(
            "/api/v1/follow-ups/", data=data, format="json"
        )

        self.assertEqual(HTTP_201_CREATED, response.status_code)

        self.assertEqual(response.data["episode"]["id"], self.episode.id)
        self.assertEqual(response.data["date"], data["date"])
        self.assertEqual(
            response.data["attendees"][0]["id"], data["attendee_ids"][0]
        )
        self.assertEqual(
            response.data["pain_severity"],
            data["pain_severity"],
        )
        self.assertEqual(
            response.data["mesh_awareness"], data["mesh_awareness"]
        )
        self.assertEqual(response.data["seroma"], data["seroma"])
        self.assertEqual(response.data["infection"], data["infection"])
        self.assertEqual(response.data["numbness"], data["numbness"])

        # check value stored in db
        follow_up = FollowUp.objects.get(id=response.data["id"])
        self.assertEqual(
            follow_up.pain_severity,
            get_text_choice_value_from_label(
                FollowUp.PainSeverityChoices.choices, data["pain_severity"]
            ),
        )

    def test_when_episode_id_does_not_exist(self):
        data = self.get_follow_up_data()
        data["episode_id"] = -1
        response = self.client.post(
            "/api/v1/follow-ups/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_when_episode_is_not_discharged_yet(self):
        data = self.get_follow_up_data()
        data["episode_id"] = EpisodeFactory().id
        response = self.client.post(
            "/api/v1/follow-ups/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_when_episode_surgery_date_is_after_follow_up_date(self):
        data = self.get_follow_up_data()
        data["date"] = "2021-12-03"
        response = self.client.post(
            "/api/v1/follow-ups/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_when_episode_discharge_date_is_after_follow_up_date(self):
        data = self.get_follow_up_data()
        data["date"] = "2022-02-05"
        response = self.client.post(
            "/api/v1/follow-ups/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)
