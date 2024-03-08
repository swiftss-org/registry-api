# Generated by Django 3.1.3 on 2023-08-08 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registry", "0033_merge_20230525_0733"),
    ]

    operations = [
        migrations.AlterField(
            model_name="episode",
            name="episode_type",
            field=models.CharField(
                choices=[
                    ("INGUINAL", "Inguinal Mesh Hernia Repair"),
                    ("INCISIONAL", "Incisional Mesh Hernia Repair"),
                    ("FEMORAL", "Femoral Mesh Hernia Repair"),
                    (
                        "UMBILICAL",
                        "Umbilical/Periumbilicial Mesh Hernia Repair",
                    ),
                    ("EPIGASTRIC", "Epigastric Hernia"),
                ],
                max_length=128,
            ),
        ),
    ]
