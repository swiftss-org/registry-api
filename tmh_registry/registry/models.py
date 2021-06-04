from django.db import models


class Hospital(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Patient(models.Model):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    national_id = models.IntegerField(null=True, blank=True, unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    day_of_birth = models.PositiveIntegerField(null=True, blank=True)
    month_of_birth = models.PositiveIntegerField(null=True, blank=True)
    year_of_birth = models.PositiveIntegerField(null=True, blank=True)
    gender = models.IntegerField(
        choices=[("GENDER_MALE", "Male"), ("GENDER_FEMALE", "Female")]
    )
    phone_1 = models.IntegerField(null=True, blank=True)
    phone_2 = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} - {self.last_name}"


class PatientHospitalMapping(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("patient", "hospital")
        verbose_name_plural = "Patient-Hospital mapping"

    def __str__(self):
        return f"{self.patient.last_name} - {self.hospital.name}"
