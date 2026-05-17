import io

from django.core.management import call_command
from django.test import TestCase
from tmh_registry.registry.factories import EpisodeFactory, FollowUpFactory
from tmh_registry.users.factories import MedicalPersonnelFactory


class TestPopulateFollowUpAttendeesCommand(TestCase):
    def setUp(self):
        self.episode = EpisodeFactory()

        # Create medical personnel
        self.attendees = [MedicalPersonnelFactory() for _ in range(5)]

    def _create_followup_with_attendees(self, num_attendees):
        followup = FollowUpFactory(
            episode=self.episode,
            primary_attendee=None,
            secondary_attendee=None,
            tertiary_attendee=None,
        )
        followup.attendees.set(self.attendees[:num_attendees])
        return followup

    def test_populate_followup_attendees(self):
        # Create followups with 0, 1, 2, 3, and 4 attendees
        fu0 = self._create_followup_with_attendees(0)
        fu1 = self._create_followup_with_attendees(1)
        fu2 = self._create_followup_with_attendees(2)
        fu3 = self._create_followup_with_attendees(3)
        fu4 = self._create_followup_with_attendees(4)

        out = io.StringIO()
        call_command("populate_followup_attendees", stdout=out)

        # Refresh from db
        fu0.refresh_from_db()
        fu1.refresh_from_db()
        fu2.refresh_from_db()
        fu3.refresh_from_db()
        fu4.refresh_from_db()

        # Check fu0
        self.assertIsNone(fu0.primary_attendee)
        self.assertIsNone(fu0.secondary_attendee)
        self.assertIsNone(fu0.tertiary_attendee)

        # Check fu1
        self.assertEqual(fu1.primary_attendee.id, self.attendees[0].id)
        self.assertIsNone(fu1.secondary_attendee)
        self.assertIsNone(fu1.tertiary_attendee)

        # Check fu2
        self.assertEqual(fu2.primary_attendee.id, self.attendees[0].id)
        self.assertEqual(fu2.secondary_attendee.id, self.attendees[1].id)
        self.assertIsNone(fu2.tertiary_attendee)

        # Check fu3
        self.assertEqual(fu3.primary_attendee.id, self.attendees[0].id)
        self.assertEqual(fu3.secondary_attendee.id, self.attendees[1].id)
        self.assertEqual(fu3.tertiary_attendee.id, self.attendees[2].id)

        # Check fu4 (should map first 3, print error, and ignore the 4th)
        self.assertEqual(fu4.primary_attendee.id, self.attendees[0].id)
        self.assertEqual(fu4.secondary_attendee.id, self.attendees[1].id)
        self.assertEqual(fu4.tertiary_attendee.id, self.attendees[2].id)

        # Check M2M field counts are untouched
        self.assertEqual(fu0.attendees.count(), 0)
        self.assertEqual(fu1.attendees.count(), 1)
        self.assertEqual(fu2.attendees.count(), 2)
        self.assertEqual(fu3.attendees.count(), 3)
        self.assertEqual(fu4.attendees.count(), 4)

        # Ensure validation passed (validation verifies no M2M counts decreased)
        self.assertIn("Validation passed", out.getvalue())
