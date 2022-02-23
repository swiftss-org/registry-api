from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.test import APIClient

from tmh_registry.users.factories import MedicalPersonnelFactory

from .....factories import EpisodeFactory, FollowUpFactory


class TestEpisodesGetDischarge(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super(TestEpisodesGetDischarge, cls).setUpClass()

        cls.episode = EpisodeFactory()

        cls.medical_personnel = MedicalPersonnelFactory()
        cls.token = Token.objects.create(user=cls.medical_personnel.user)

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_when_episode_does_not_exist(self):
        response = self.client.get("/api/v1/episodes/-1/follow-ups/")

        self.assertEqual(HTTP_404_NOT_FOUND, response.status_code)

    def test_when_episode_exists_but_follow_ups_do_not(self):
        response = self.client.get(
            f"/api/v1/episodes/{self.episode.id}/follow-ups/"
        )

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_successful(self):
        follow_ups = FollowUpFactory.create_batch(5, episode=self.episode)
        FollowUpFactory.create_batch(5)  # irrelevant data

        response = self.client.get(
            f"/api/v1/episodes/{self.episode.id}/follow-ups/"
        )

        self.assertEqual(HTTP_200_OK, response.status_code)

        self.assertEqual(len(response.data), 5)
        self.assertCountEqual(
            [follow_up["id"] for follow_up in response.data],
            [follow_up.id for follow_up in follow_ups],
        )
