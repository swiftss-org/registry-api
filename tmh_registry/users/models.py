from django.contrib.auth.models import User
from django.db import models


class MedicalPersonnel(models.Model):
    """
    Model for Medical Personnel which is a proxy model of User
    """

    SURGEON = "SURGEON"
    LEAD_SURGEON = "LEAD_SURGEON"
    NATIONAL_LEAD = "NATIONAL_LEAD"
    LEVEL_CHOICES = (
        (SURGEON, "Surgeon"),
        (LEAD_SURGEON, "Lead Surgeon"),
        (NATIONAL_LEAD, "National Lead"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name="medical_personnel",
    )

    level = models.CharField(
        max_length=255,
        choices=LEVEL_CHOICES,
        default=LEAD_SURGEON,
    )

    class Meta:
        verbose_name_plural = "Medical Personnel"

    def __str__(self):
        return f"({self.get_level_display()}) {self.user.username}"

    def get_level_display(self):
        return [
            level_tuple[1]
            for level_tuple in self.LEVEL_CHOICES
            if level_tuple[0] == self.level
        ]
