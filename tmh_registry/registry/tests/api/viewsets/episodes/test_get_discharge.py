from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.test import APIClient
from tmh_registry.users.factories import MedicalPersonnelFactory

from .....factories import DischargeFactory, EpisodeFactory


class TestEpisodesGetDischarge(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.episode = EpisodeFactory()
        cls.medical_personnel = MedicalPersonnelFactory()

    def setUp(self) -> None:
        self.token = Token.objects.create(user=self.medical_personnel.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_when_episode_does_not_exist(self):
        response = self.client.get("/api/v1/episodes/-1/discharge/")

        self.assertEqual(HTTP_404_NOT_FOUND, response.status_code)

    def test_when_episode_exists_but_discharge_does_not(self):
        response = self.client.get(
            f"/api/v1/episodes/{self.episode.id}/discharge/"
        )

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual({}, response.data)

    def test_successful(self):
        discharge = DischargeFactory(episode=self.episode)

        response = self.client.get(
            f"/api/v1/episodes/{self.episode.id}/discharge/"
        )

        self.assertEqual(HTTP_200_OK, response.status_code)

        self.assertEqual(response.data["id"], discharge.id)
        self.assertEqual(response.data["episode"]["id"], discharge.episode.id)
