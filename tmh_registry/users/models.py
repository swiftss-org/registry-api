from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """
    Model for Profile which is a proxy model of User
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        default=None,
        null=True,
    )

