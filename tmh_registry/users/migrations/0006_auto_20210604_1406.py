# Generated by Django 3.1.3 on 2021-06-04 14:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_medicalpersonnel_level"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="medicalpersonnel",
            options={"verbose_name_plural": "Medical Personnel"},
        ),
    ]