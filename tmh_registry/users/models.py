from django.contrib.auth.models import User
from django.db import models
from django.db.models.enums import TextChoices


class MedicalPersonnel(models.Model):
    """
    Model for Medical Personnel which is a proxy model of User
    """

    class Level(TextChoices):
        SURGEON = ("SURGEON", "Surgeon")
        LEAD_SURGEON = ("LEAD_SURGEON", "Lead Surgeon")
        NATIONAL_LEAD = ("NATIONAL_LEAD", "National Lead")

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name="medical_personnel",
    )

    level = models.CharField(
        max_length=255,
        choices=Level.choices,
        default=Level.LEAD_SURGEON,
    )

    class Meta:
        verbose_name_plural = "Medical Personnel"

    def __str__(self):
        return f"({self.get_level_display()}) {self.user.username}"
