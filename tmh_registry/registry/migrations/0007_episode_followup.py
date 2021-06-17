# Generated by Django 3.1.3 on 2021-06-17 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_auto_20210611_1126"),
        ("registry", "0006_auto_20210609_1559"),
    ]

    operations = [
        migrations.CreateModel(
            name="Episode",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("surgery_date", models.DateField(blank=True, null=True)),
                ("discharge_date", models.DateField(blank=True, null=True)),
                (
                    "episode_type",
                    models.CharField(
                        choices=[
                            ("INGUINAL", "Inguinal Mesh Hernia Repair"),
                            ("INCISIONAL", "Incisional Mesh Hernia Repair"),
                            ("FEMORAL", "Femoral Mesh Hernia Repair"),
                            ("HIATUS", "Hiatus Mesh Hernia Repair"),
                            (
                                "UMBILICAL",
                                "Umbilical/Periumbilicial Mesh Hernia Repair",
                            ),
                        ],
                        max_length=128,
                    ),
                ),
                ("comments", models.TextField(blank=True, null=True)),
                (
                    "cepod",
                    models.CharField(
                        choices=[
                            ("PLANNED", "Planned"),
                            ("EMERGENCY", "Emergency"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "side",
                    models.CharField(
                        choices=[("LEFT", "Left"), ("RIGHT", "Right")],
                        max_length=16,
                    ),
                ),
                (
                    "occurence",
                    models.CharField(
                        choices=[
                            ("PRIMARY", "Primary"),
                            ("RECURRENT", "Recurrent"),
                            ("RERECURRENT", "Rerecurrent"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("DIRECT", "Direct"),
                            ("INDIRECT", "Indirect"),
                            ("PANTALOON", "Pantaloon"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "complexity",
                    models.CharField(
                        choices=[
                            ("SIMPLE", "Simple"),
                            ("INCARCERATED", "Incarcerated"),
                            ("OBSTRUCTED", "Obstructed"),
                            ("STRANGULATED", "Strangulated"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "mesh_type",
                    models.CharField(
                        choices=[
                            ("TNMHP", "TNMHP Mesh"),
                            ("KCMC", "KCMC Generic Mesh"),
                            ("COMMERCIAL", "Commercial Mesh"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "anaesthetic_type",
                    models.CharField(
                        choices=[
                            ("LOCAL", "Local Anaesthetic"),
                            ("SPINAL", "Spinal Anaesthetic"),
                            ("GENERAL", "General Anaesthetic"),
                        ],
                        max_length=16,
                    ),
                ),
                ("diathermy_used", models.BooleanField()),
                (
                    "patient_hospital_mapping",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="registry.patienthospitalmapping",
                    ),
                ),
                (
                    "surgeons",
                    models.ManyToManyField(to="users.MedicalPersonnel"),
                ),
            ],
            options={
                "verbose_name_plural": "Episodes",
            },
        ),
        migrations.CreateModel(
            name="FollowUp",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("follow_up_date", models.DateField()),
                (
                    "pain_severity",
                    models.CharField(
                        choices=[
                            ("NO_PAIN", "No Pain"),
                            ("MINIMAL", "Minimal"),
                            ("MILD", "Mild"),
                            ("MODERATE", "Moderate"),
                            ("SEVERE", "Severe"),
                        ],
                        max_length=16,
                    ),
                ),
                ("mesh_awareness", models.BooleanField()),
                ("seroma", models.BooleanField()),
                ("infection", models.BooleanField()),
                ("numbness", models.BooleanField()),
                (
                    "attendees",
                    models.ManyToManyField(to="users.MedicalPersonnel"),
                ),
                (
                    "episode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="registry.episode",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Follow Ups",
            },
        ),
    ]
