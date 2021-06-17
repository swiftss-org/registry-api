import datetime
from enum import Enum

from django.db import models

from ..users.models import MedicalPersonnel


class Hospital(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Patient(models.Model):
    class Gender(Enum):
        GENDER_MALE = "Male"
        GENDER_FEMALE = "Female"

    full_name = models.CharField(max_length=255)
    national_id = models.CharField(
        max_length=20, null=True, blank=True, unique=True
    )
    day_of_birth = models.PositiveIntegerField(null=True, blank=True)
    month_of_birth = models.PositiveIntegerField(null=True, blank=True)
    year_of_birth = models.PositiveIntegerField()
    gender = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        choices=[(gender.value, gender.value) for gender in Gender],
    )
    phone_1 = models.CharField(max_length=16, null=True, blank=True)
    phone_2 = models.CharField(max_length=16, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name}"

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


class Episode(models.Model):

    INGUINAL = "INGUINAL"
    INCISIONAL = "INCISIONAL"
    FEMORAL = "FEMORAL"
    HIATUS = "HIATUS"
    UMBILICAL = "UMBILICAL"
    EPISODE_CHOICES = (
        (INGUINAL, "Inguinal Mesh Hernia Repair"),
        (INCISIONAL, "Incisional Mesh Hernia Repair"),
        (FEMORAL, "Femoral Mesh Hernia Repair"),
        (HIATUS, "Hiatus Mesh Hernia Repair"),
        (UMBILICAL, "Umbilical/Periumbilicial Mesh Hernia Repair"),
    )

    PLANNED = "PLANNED"
    EMERGENCY = "EMERGENCY"
    CEPOD_CHOICES = (
        (PLANNED, "Planned"),
        (EMERGENCY, "Emergency"),
    )

    LEFT = "LEFT"
    RIGHT = "RIGHT"
    SIDE_CHOICES = ((LEFT, "Left"), (RIGHT, "Right"))

    PRIMARY = "PRIMARY"
    RECURRENT = "RECURRENT"
    RERECURRENT = "RERECURRENT"
    OCCURENCE_CHOICES = (
        (PRIMARY, "Primary"),
        (RECURRENT, "Recurrent"),
        (RERECURRENT, "Rerecurrent"),
    )

    DIRECT = "DIRECT"
    INDIRECT = "INDIRECT"
    PANTALOON = "PANTALOON"
    TYPE_CHOICES = (
        (DIRECT, "Direct"),
        (INDIRECT, "Indirect"),
        (PANTALOON, "Pantaloon"),
    )

    SIMPLE = "SIMPLE"
    INCARCERATED = "INCARCERATED"
    OBSTRUCTED = "OBSTRUCTED"
    STRANGULATED = "STRANGULATED"
    COMPLEXITY_CHOICES = (
        (SIMPLE, "Simple"),
        (INCARCERATED, "Incarcerated"),
        (OBSTRUCTED, "Obstructed"),
        (STRANGULATED, "Strangulated"),
    )

    TNMHP = "TNMHP"
    KCMC = "KCMC"
    COMMERCIAL = "COMMERCIAL"
    MESH_TYPE_CHOICES = (
        (TNMHP, "TNMHP Mesh"),
        (KCMC, "KCMC Generic Mesh"),
        (COMMERCIAL, "Commercial Mesh"),
    )

    LOCAL = "LOCAL"
    SPINAL = "SPINAL"
    GENERAL = "GENERAL"
    ANAESTHETIC_TYPE_CHOICES = (
        (LOCAL, "Local Anaesthetic"),
        (SPINAL, "Spinal Anaesthetic"),
        (GENERAL, "General Anaesthetic"),
    )

    patient_hospital_mapping = models.ForeignKey(
        PatientHospitalMapping, on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)
    surgery_date = models.DateField(null=True, blank=True)
    discharge_date = models.DateField(null=True, blank=True)
    episode_type = models.CharField(max_length=128, choices=EPISODE_CHOICES)
    surgeons = models.ManyToManyField(MedicalPersonnel)
    comments = models.TextField(null=True, blank=True)
    cepod = models.CharField(max_length=16, choices=CEPOD_CHOICES)
    side = models.CharField(max_length=16, choices=SIDE_CHOICES)
    occurence = models.CharField(max_length=16, choices=OCCURENCE_CHOICES)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    complexity = models.CharField(max_length=16, choices=COMPLEXITY_CHOICES)
    mesh_type = models.CharField(max_length=16, choices=MESH_TYPE_CHOICES)
    anaesthetic_type = models.CharField(
        max_length=16, choices=ANAESTHETIC_TYPE_CHOICES
    )
    diathermy_used = models.BooleanField()

    def __str__(self):
        return f"({self.episode_type}) {self.patient_hospital_mapping.patient.first_name} {self.patient_hospital_mapping.patient.last_name}"

    class Meta:
        verbose_name_plural = "Episodes"


class FollowUp(models.Model):

    NO_PAIN = "NO_PAIN"
    MINIMAL = "MINIMAL"
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    PAIN_SEVERITY_CHOICES = (
        (NO_PAIN, "No Pain"),
        (MINIMAL, "Minimal"),
        (MILD, "Mild"),
        (MODERATE, "Moderate"),
        (SEVERE, "Severe"),
    )

    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    follow_up_date = models.DateField()
    pain_severity = models.CharField(
        max_length=16, choices=PAIN_SEVERITY_CHOICES
    )
    attendees = models.ManyToManyField(MedicalPersonnel)
    mesh_awareness = models.BooleanField()
    seroma = models.BooleanField()
    infection = models.BooleanField()
    numbness = models.BooleanField()

    def __str__(self):
        return f"[{self.follow_up_date}] {self.episode}"

    class Meta:
        verbose_name_plural = "Follow Ups"
