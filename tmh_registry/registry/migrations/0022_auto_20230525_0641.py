# Generated by Django 3.1.3 on 2023-05-25 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registry", "0021_auto_20230213_1528"),
    ]

    operations = [
        migrations.AlterField(
            model_name="episode",
            name="mesh_type",
            field=models.CharField(
                choices=[
                    ("TNMHP", "TNMHP Mesh"),
                    ("KCMC", "KCMC Generic Mesh"),
                    ("COMMERCIAL", "Commercial Mesh"),
                    ("INTERNATIONAL", "Hernia International Mesh"),
                ],
                max_length=16,
            ),
        ),
    ]
