import os

from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_superuser(apps, schema_editor):
    if all(
        [
            os.environ.get("ADMIN_PASSWORD"),
            os.environ.get("ADMIN_EMAIL"),
        ]
    ):
        superuser = apps.get_model("auth", "User").objects.create(
            is_active=True,
            is_superuser=True,
            is_staff=True,
            username=os.environ["ADMIN_EMAIL"],
            email=os.environ["ADMIN_EMAIL"],
            password=make_password(os.environ["ADMIN_PASSWORD"]),
        )
        superuser.save()
        profile = apps.get_model("users", "Profile").objects.create(
            user=superuser
        )
        profile.save()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [migrations.RunPython(create_superuser)]
