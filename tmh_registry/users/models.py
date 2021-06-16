from django.contrib.auth.models import User
from django.db import models


class MedicalPersonnel(models.Model):
    """
    Model for Profile which is a proxy model of User
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name="medical_personnel",
    )

    level = models.CharField(
        max_length=255,
        choices=[("LEAD_SURGEON", "Lead Surgeon")],
        default="Lead Surgeon",
    )

    class Meta:
        verbose_name_plural = "Medical Personnel"

    def __str__(self):
        return self.user.username
