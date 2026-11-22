from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db.models import Count
from tmh_registry.registry.models import Episode


class Command(BaseCommand):
    help = (
        "Populates the primary, secondary, and tertiary surgeon fields "
        "from the surgeons ManyToMany field in natural insertion order."
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
            self.stdout.write("Starting surgeon migration...")

        episodes = (
            Episode.objects.select_related(
                "patient_hospital_mapping__patient",
                "patient_hospital_mapping__hospital",
            )
            .prefetch_related("surgeons")
            .all()
        )

        through_records = (
            Episode.surgeons.through.objects.filter(episode__in=episodes)
            .order_by("id")
            .select_related("medicalpersonnel__user")
        )
        natural_surgeons_by_episode = defaultdict(list)
        for record in through_records:
            natural_surgeons_by_episode[record.episode_id].append(
                record.medicalpersonnel
            )

        episodes_to_update = []
        original_surgeon_counts = {}

        for episode in episodes:
            surgeons = natural_surgeons_by_episode[episode.id]
            original_surgeon_counts[episode.id] = len(surgeons)

            if len(surgeons) > 0:
                episode.primary_surgeon = surgeons[0]
                if len(surgeons) > 1:
                    patient = episode.patient_hospital_mapping.patient
                    hospital = episode.patient_hospital_mapping.hospital
                    ui_path = f"/patients/{hospital.id}/{patient.id}/episodes/{episode.id}"
                    admin_path = (
                        f"/admin/registry/episode/{episode.id}/change/"
                    )

                    self.stdout.write(
                        self.style.ERROR(
                            f"\n"
                            f"---- Episode {episode.id} -- {episode.surgery_date} -- {episode.episode_type} ----\n"
                            f"[Patient ID: {patient.id} ({patient.full_name})] \n"
                            f"Has {len(surgeons)} surgeons.\n"
                            f"  UI Path:    {ui_path}\n"
                            f"  Admin Path: {admin_path}\n"
                            f"  Natural Order:"
                        )
                    )
                    for idx, surgeon in enumerate(surgeons, start=1):
                        role = (
                            "Main Operating"
                            if idx == 1
                            else (
                                "Secondary"
                                if idx == 2
                                else (
                                    "Supervising"
                                    if idx == 3
                                    else f"Extra #{idx}"
                                )
                            )
                        )
                        user = surgeon.user
                        full_name = (
                            f"{user.first_name} {user.last_name}".strip()
                            or "(No name set)"
                        )
                        self.stdout.write(
                            f"    {idx}. [{role}] MP ID: {surgeon.id} | User ID: {user.id} ({user.username} - {full_name})"
                        )
                    episode.secondary_surgeon = surgeons[1]
                if len(surgeons) > 2:
                    episode.tertiary_surgeon = surgeons[2]

                episodes_to_update.append(episode)

        if report_only:
            self.stdout.write(
                self.style.WARNING(
                    f"[REPORT-ONLY] {len(episodes_to_update)} episodes would be updated."
                )
            )
            self.stdout.write(
                self.style.SUCCESS("Report finished (no changes made).")
            )
            return

        if episodes_to_update:
            Episode.objects.bulk_update(
                episodes_to_update,
                [
                    "primary_surgeon",
                    "secondary_surgeon",
                    "tertiary_surgeon",
                ],
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully updated {len(episodes_to_update)} episodes."
                )
            )
            for episode in episodes_to_update:
                self.stdout.write(
                    self.style.SUCCESS(f"Episode {episode.id} was updated.")
                )
        else:
            self.stdout.write("No episodes needed updating.")

        # Validation Checks
        self.stdout.write("Running validation checks...")

        # 1. Verify that the total number of episodes with surgeons in the ManyToMany field matches
        # the number of episodes that now have a primary_surgeon assigned.
        episodes_with_m2m_surgeons = (
            Episode.objects.annotate(num_surgeons=Count("surgeons"))
            .filter(num_surgeons__gt=0)
            .count()
        )
        episodes_with_primary_surgeon = Episode.objects.filter(
            primary_surgeon__isnull=False
        ).count()

        if episodes_with_m2m_surgeons == episodes_with_primary_surgeon:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Validation passed: Number of episodes with surgeons ({episodes_with_m2m_surgeons}) matches episodes with primary_surgeon."
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Validation failed: {episodes_with_m2m_surgeons} episodes have surgeons in M2M, but {episodes_with_primary_surgeon} have a primary_surgeon assigned."
                )
            )
            episodes_with_m2m_surgeons_only = Episode.objects.annotate(
                num_surgeons=Count("surgeons")
            ).filter(num_surgeons__gt=0, primary_surgeon__isnull=True)
            for episode in episodes_with_m2m_surgeons_only:
                self.stdout.write(
                    self.style.ERROR(
                        f"Episode {episode.id} has surgeons in M2M but not primary_surgeon."
                    )
                )

        # 2. Validate that the surgeons ManyToMany field count has not decreased for any episode
        validation_failed = False
        updated_episodes = Episode.objects.prefetch_related("surgeons").all()
        for episode in updated_episodes:
            current_count = episode.surgeons.count()
            original_count = original_surgeon_counts.get(episode.id, 0)
            if current_count < original_count:
                self.stdout.write(
                    self.style.ERROR(
                        f"Validation failed for Episode {episode.id}: Surgeon count decreased from {original_count} to {current_count}."
                    )
                )
                validation_failed = True

        if not validation_failed:
            self.stdout.write(
                self.style.SUCCESS(
                    "Validation passed: No episodes lost surgeons from the ManyToMany field."
                )
            )

        self.stdout.write(self.style.SUCCESS("Migration script finished."))
