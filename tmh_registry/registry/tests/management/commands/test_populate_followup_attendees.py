import io

from django.core.management import call_command
from django.test import TestCase
from tmh_registry.registry.factories import (
    EpisodeFactory,
    FollowUpFactory,
    HospitalFactory,
    PatientFactory,
    PatientHospitalMappingFactory,
)
from tmh_registry.users.factories import MedicalPersonnelFactory


class TestPopulateFollowUpAttendeesCommand(TestCase):
    def setUp(self):
        self.hospital = HospitalFactory()
        self.patient = PatientFactory()
        self.mapping = PatientHospitalMappingFactory(
            patient=self.patient, hospital=self.hospital
        )
        self.episode = EpisodeFactory(patient_hospital_mapping=self.mapping)

        # Create medical personnel
        self.attendees = [MedicalPersonnelFactory() for _ in range(5)]

    def _create_followup_with_attendees(self, num_attendees):
        followup = FollowUpFactory(
            episode=self.episode,
            primary_attendee=None,
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

        # Check fu1
        self.assertEqual(fu1.primary_attendee.id, self.attendees[0].id)

        # Check fu2
        self.assertEqual(fu2.primary_attendee.id, self.attendees[0].id)

        # Check fu3
        self.assertEqual(fu3.primary_attendee.id, self.attendees[0].id)

        # Check fu4
        self.assertEqual(fu4.primary_attendee.id, self.attendees[0].id)

        # Check M2M field counts are untouched
        self.assertEqual(fu0.attendees.count(), 0)
        self.assertEqual(fu1.attendees.count(), 1)
        self.assertEqual(fu2.attendees.count(), 2)
        self.assertEqual(fu3.attendees.count(), 3)
        self.assertEqual(fu4.attendees.count(), 4)

        # Ensure validation passed (validation verifies no M2M counts decreased)
        self.assertIn("Validation passed", out.getvalue())

    def test_populate_followup_attendees_report_only(self):
        fu = self._create_followup_with_attendees(2)

        out = io.StringIO()
        call_command(
            "populate_followup_attendees", report_only=True, stdout=out
        )

        fu.refresh_from_db()
        self.assertIsNone(fu.primary_attendee)

        output = out.getvalue()
        self.assertIn("Running in --report-only mode", output)
        self.assertIn("[REPORT-ONLY] 1 follow-ups would be updated", output)
        self.assertIn(
            f"/patients/{self.hospital.id}/{self.patient.id}/episodes/{self.episode.id}",
            output,
        )
        self.assertIn(f"/admin/registry/followup/{fu.id}/change/", output)
        self.assertIn(f"Patient ID: {self.patient.id}", output)

    def test_populate_followup_attendees_natural_order(self):
        ordered_attendees = [
            self.attendees[3],
            self.attendees[1],
        ]
        fu = FollowUpFactory(
            episode=self.episode,
            primary_attendee=None,
        )
        for attendee in ordered_attendees:
            fu.attendees.add(attendee)

        out = io.StringIO()
        call_command("populate_followup_attendees", stdout=out)

        fu.refresh_from_db()
        self.assertEqual(fu.primary_attendee.id, self.attendees[3].id)
