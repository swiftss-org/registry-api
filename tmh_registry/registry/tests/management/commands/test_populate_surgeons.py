import io
from django.core.management import call_command
from django.test import TestCase
from tmh_registry.registry.models import Episode
from tmh_registry.registry.factories import EpisodeFactory, HospitalFactory, PatientFactory, PatientHospitalMappingFactory
from tmh_registry.users.factories import MedicalPersonnelFactory


class TestPopulateSurgeonsCommand(TestCase):
    def setUp(self):
        self.hospital = HospitalFactory()
        self.patient = PatientFactory()
        self.mapping = PatientHospitalMappingFactory(patient=self.patient, hospital=self.hospital)
        
        # Create medical personnel
        self.surgeons = [MedicalPersonnelFactory() for _ in range(5)]

    def _create_episode_with_surgeons(self, num_surgeons):
        episode = EpisodeFactory(
            patient_hospital_mapping=self.mapping,
            primary_surgeon=None,
            secondary_surgeon=None,
            tertiary_surgeon=None,
        )
        episode.surgeons.set(self.surgeons[:num_surgeons])
        return episode

    def test_populate_surgeons(self):
        # Create episodes with 0, 1, 2, 3, and 4 surgeons
        ep0 = self._create_episode_with_surgeons(0)
        ep1 = self._create_episode_with_surgeons(1)
        ep2 = self._create_episode_with_surgeons(2)
        ep3 = self._create_episode_with_surgeons(3)
        ep4 = self._create_episode_with_surgeons(4)

        out = io.StringIO()
        call_command("populate_surgeons", stdout=out)
        
        # Refresh from db
        ep0.refresh_from_db()
        ep1.refresh_from_db()
        ep2.refresh_from_db()
        ep3.refresh_from_db()
        ep4.refresh_from_db()

        # Check ep0
        self.assertIsNone(ep0.primary_surgeon)
        self.assertIsNone(ep0.secondary_surgeon)
        self.assertIsNone(ep0.tertiary_surgeon)

        # Check ep1
        self.assertEqual(ep1.primary_surgeon.id, self.surgeons[0].id)
        self.assertIsNone(ep1.secondary_surgeon)
        self.assertIsNone(ep1.tertiary_surgeon)

        # Check ep2
        self.assertEqual(ep2.primary_surgeon.id, self.surgeons[0].id)
        self.assertEqual(ep2.secondary_surgeon.id, self.surgeons[1].id)
        self.assertIsNone(ep2.tertiary_surgeon)

        # Check ep3
        self.assertEqual(ep3.primary_surgeon.id, self.surgeons[0].id)
        self.assertEqual(ep3.secondary_surgeon.id, self.surgeons[1].id)
        self.assertEqual(ep3.tertiary_surgeon.id, self.surgeons[2].id)

        # Check ep4 (should map first 3, print error, and ignore the 4th)
        self.assertEqual(ep4.primary_surgeon.id, self.surgeons[0].id)
        self.assertEqual(ep4.secondary_surgeon.id, self.surgeons[1].id)
        self.assertEqual(ep4.tertiary_surgeon.id, self.surgeons[2].id)
        
        # Check M2M field counts are untouched
        self.assertEqual(ep0.surgeons.count(), 0)
        self.assertEqual(ep1.surgeons.count(), 1)
        self.assertEqual(ep2.surgeons.count(), 2)
        self.assertEqual(ep3.surgeons.count(), 3)
        self.assertEqual(ep4.surgeons.count(), 4)
        
        # Ensure validation passed (validation verifies no M2M counts decreased)
        self.assertIn("Validation passed", out.getvalue())
