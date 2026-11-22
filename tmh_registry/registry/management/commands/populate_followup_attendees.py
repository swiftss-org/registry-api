from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db.models import Count
from tmh_registry.registry.models import FollowUp


class Command(BaseCommand):
    help = (
        "Populates the primary attendee field from the attendees "
        "ManyToMany field in FollowUp in natural insertion order."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--report-only",
            action="store_true",
            help="Generate the migration report without applying database changes.",
        )

    def handle(self, *args, **options):
        report_only = options.get("report_only", False)
        if report_only:
            self.stdout.write(
                self.style.WARNING(
                    "Running in --report-only mode. Database will NOT be updated."
                )
            )
        else:
            self.stdout.write("Starting FollowUp attendee migration...")

        followups = (
            FollowUp.objects.select_related(
                "episode__patient_hospital_mapping__patient",
                "episode__patient_hospital_mapping__hospital",
            )
            .prefetch_related("attendees")
            .all()
        )

        through_records = (
            FollowUp.attendees.through.objects.filter(followup__in=followups)
            .order_by("id")
            .select_related("medicalpersonnel__user")
        )
        natural_attendees_by_followup = defaultdict(list)
        for record in through_records:
            natural_attendees_by_followup[record.followup_id].append(
                record.medicalpersonnel
            )

        followups_to_update = []
        original_attendee_counts = {}

        for followup in followups:
            attendees = natural_attendees_by_followup[followup.id]
            original_attendee_counts[followup.id] = len(attendees)

            if len(attendees) > 0:
                followup.primary_attendee = attendees[0]
                if len(attendees) > 1:
                    patient = followup.episode.patient_hospital_mapping.patient
                    hospital = (
                        followup.episode.patient_hospital_mapping.hospital
                    )
                    ui_path = f"/patients/{hospital.id}/{patient.id}/episodes/{followup.episode_id}"
                    admin_path = (
                        f"/admin/registry/followup/{followup.id}/change/"
                    )

                    self.stdout.write(
                        self.style.ERROR(
                            f"---- FollowUp {followup.id} -- Episode {followup.episode_id} -- {followup.episode.episode_type} ----\n"
                            f"[Patient ID: {patient.id} ({patient.full_name})]\n"
                            f"Has {len(attendees)} attendees.\n"
                            f"  UI Path:    {ui_path}\n"
                            f"  Admin Path: {admin_path}\n"
                            f"  Natural Order:"
                        )
                    )
                    for idx, attendee in enumerate(attendees, start=1):
                        role = (
                            "Primary Attendee" if idx == 1 else f"Extra #{idx}"
                        )
                        user = attendee.user
                        full_name = (
                            f"{user.first_name} {user.last_name}".strip()
                            or "(No name set)"
                        )
                        self.stdout.write(
                            f"    {idx}. [{role}] MP ID: {attendee.id} | User ID: {user.id} ({user.username} - {full_name})"
                        )
                followups_to_update.append(followup)

        if report_only:
            self.stdout.write(
                self.style.WARNING(
                    f"[REPORT-ONLY] {len(followups_to_update)} follow-ups would be updated."
                )
            )
            self.stdout.write(
                self.style.SUCCESS("Report finished (no changes made).")
            )
            return

        if followups_to_update:
            FollowUp.objects.bulk_update(
                followups_to_update,
                [
                    "primary_attendee",
                ],
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully updated {len(followups_to_update)} follow-ups."
                )
            )
            for followup in followups_to_update:
                self.stdout.write(
                    self.style.SUCCESS(f"FollowUp {followup.id} was updated.")
                )
        else:
            self.stdout.write("No follow-ups needed updating.")

        # Validation Checks
        self.stdout.write("Running validation checks...")

        # 1. Verify that the total number of follow-ups with attendees in the ManyToMany field matches
        # the number of follow-ups that now have a primary_attendee assigned.
        followups_with_m2m_attendees = (
            FollowUp.objects.annotate(num_attendees=Count("attendees"))
            .filter(num_attendees__gt=0)
            .count()
        )
        followups_with_primary_attendee = FollowUp.objects.filter(
            primary_attendee__isnull=False
        ).count()

        if followups_with_m2m_attendees == followups_with_primary_attendee:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Validation passed: Number of follow-ups with attendees ({followups_with_m2m_attendees}) matches follow-ups with primary_attendee."
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Validation failed: {followups_with_m2m_attendees} follow-ups have attendees in M2M, but {followups_with_primary_attendee} have a primary_attendee assigned."
                )
            )
            followups_with_m2m_only = FollowUp.objects.annotate(
                num_attendees=Count("attendees")
            ).filter(num_attendees__gt=0, primary_attendee__isnull=True)
            for followup in followups_with_m2m_only:
                self.stdout.write(
                    self.style.ERROR(
                        f"FollowUp {followup.id} has attendees in M2M but not primary_attendee."
                    )
                )

        # 2. Validate that the attendees ManyToMany field count has not decreased for any follow-up
        validation_failed = False
        updated_followups = FollowUp.objects.prefetch_related(
            "attendees"
        ).all()
        for followup in updated_followups:
            current_count = followup.attendees.count()
            original_count = original_attendee_counts.get(followup.id, 0)
            if current_count < original_count:
                self.stdout.write(
                    self.style.ERROR(
                        f"Validation failed for FollowUp {followup.id}: Attendee count decreased from {original_count} to {current_count}."
                    )
                )
                validation_failed = True

        if not validation_failed:
            self.stdout.write(
                self.style.SUCCESS(
                    "Validation passed: No follow-ups lost attendees from the ManyToMany field."
                )
            )

        self.stdout.write(self.style.SUCCESS("Migration script finished."))
