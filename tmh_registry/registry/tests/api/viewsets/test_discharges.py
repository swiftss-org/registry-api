from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.test import APIClient

from tmh_registry.registry.factories import DischargeFactory, EpisodeFactory
from tmh_registry.users.factories import MedicalPersonnelFactory


class TestDischargeCreate(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super(TestDischargeCreate, cls).setUpClass()

        cls.episode = EpisodeFactory(surgery_date="2022-01-23")

        cls.medical_personnel = MedicalPersonnelFactory()
        cls.token = Token.objects.create(user=cls.medical_personnel.user)

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def get_discharge_data(self):
        return {
            "episode_id": self.episode.id,
            "date": "2022-02-22",
            "aware_of_mesh": True,
            "infection": False,
        }

    def test_successful(self):
        data = self.get_discharge_data()
        response = self.client.post(
            "/api/v1/discharges/", data=data, format="json"
        )

        self.assertEqual(HTTP_201_CREATED, response.status_code)

        self.assertEqual(response.data["episode"]["id"], self.episode.id)
        self.assertEqual(response.data["date"], data["date"])
        self.assertEqual(response.data["aware_of_mesh"], data["aware_of_mesh"])
        self.assertEqual(response.data["infection"], data["infection"])

    def test_when_episode_id_does_not_exist(self):
        data = self.get_discharge_data()
        data["episode_id"] = -1
        response = self.client.post(
            "/api/v1/discharges/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_when_episode_is_already_discharged(self):
        DischargeFactory(episode=self.episode, date="2022-02-22")
        data = self.get_discharge_data()
        response = self.client.post(
            "/api/v1/discharges/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_when_episode_surgery_date_is_after_discharge_date(self):
        data = self.get_discharge_data()
        data["date"] = "2021-12-03"
        response = self.client.post(
            "/api/v1/discharges/", data=data, format="json"
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)
