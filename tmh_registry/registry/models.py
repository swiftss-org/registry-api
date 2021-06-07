import datetime

from django.db import models


class Hospital(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Patient(models.Model):
    GENDER_MALE = 0
    GENDER_FEMALE = 1
    GENDER_CHOICES = [(GENDER_MALE, "Male"), (GENDER_FEMALE, "Female")]

    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    national_id = models.CharField(
        max_length=20, null=True, blank=True, unique=True
    )
    day_of_birth = models.PositiveIntegerField(null=True, blank=True)
    month_of_birth = models.PositiveIntegerField(null=True, blank=True)
    year_of_birth = models.PositiveIntegerField(null=True, blank=True)
    gender = models.IntegerField(choices=GENDER_CHOICES)
    phone_1 = models.CharField(max_length=16, null=True, blank=True)
    phone_2 = models.CharField(max_length=16, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} - {self.last_name}"

    @property
    def age(self):
        return datetime.datetime.today().year - self.year_of_birth

    @staticmethod
    def get_year_of_birth_from_age(age):
        return datetime.datetime.today().year - age


class PatientHospitalMapping(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("patient", "hospital")
        verbose_name_plural = "Patient-Hospital mapping"

    def __str__(self):
        return f"{self.patient.last_name} - {self.hospital.name}"
