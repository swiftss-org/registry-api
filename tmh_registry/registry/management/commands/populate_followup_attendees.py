from django.core.management.base import BaseCommand
from django.db.models import Count
from tmh_registry.registry.models import FollowUp


class Command(BaseCommand):
    help = "Populates the primary, secondary, and tertiary attendee fields from the attendees ManyToMany field in FollowUp."

    def handle(self, *args, **options):
        self.stdout.write("Starting FollowUp attendee migration...")

        followups = FollowUp.objects.prefetch_related("attendees").all()
        followups_to_update = []
        original_attendee_counts = {}

        for followup in followups:
            attendees = list(followup.attendees.all().order_by("id"))
            original_attendee_counts[followup.id] = len(attendees)

            if len(attendees) > 0:
                followup.primary_attendee = attendees[0]
                if len(attendees) > 1:
                    patient_name = (
                        followup.episode.patient_hospital_mapping.patient.full_name
                    )
                    self.stdout.write(
                        self.style.ERROR(
                            f"FollowUp {followup.id} [Episode ({followup.episode.episode_type}) {patient_name} | FollowUp {followup.id}] has more than 1 attendee. It has {len(attendees)} attendees."
                        )
                    )
                followups_to_update.append(followup)

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
