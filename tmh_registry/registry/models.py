import datetime

from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    ForeignKey,
    ManyToManyField,
    Model,
    OneToOneField,
    PositiveIntegerField,
    TextChoices,
    TextField,
)

from tmh_registry.common.models import TimeStampMixin
from tmh_registry.users.models import MedicalPersonnel


class Hospital(Model):
    name = CharField(max_length=255, null=True, blank=True)
    address = CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Patient(TimeStampMixin):
    class Gender(TextChoices):
        MALE = ("Male", "Male")
        FEMALE = ("Female", "Female")

    full_name = CharField(max_length=255)
    national_id = CharField(max_length=20, null=True, blank=True, unique=True)
    day_of_birth = PositiveIntegerField(null=True, blank=True)
    month_of_birth = PositiveIntegerField(null=True, blank=True)
    year_of_birth = PositiveIntegerField()
    gender = CharField(
        max_length=32,
        null=True,
        blank=True,
        choices=Gender.choices,
    )
    phone_1 = CharField(max_length=16, null=True, blank=True)
    phone_2 = CharField(max_length=16, null=True, blank=True)
    address = CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name}"

    @property
    def age(self):
        return datetime.datetime.today().year - self.year_of_birth

    @staticmethod
    def get_year_of_birth_from_age(age):
        return datetime.datetime.today().year - age


class PatientHospitalMapping(Model):
    patient = ForeignKey(
        Patient, on_delete=CASCADE, related_name="hospital_mappings"
    )
    hospital = ForeignKey(
        Hospital, on_delete=CASCADE, related_name="patient_mappings"
    )
    patient_hospital_id = CharField(max_length=256)

    class Meta:
        unique_together = (
            ("patient", "hospital"),
            ("hospital", "patient_hospital_id"),
        )
        verbose_name_plural = "Patient-Hospital mappings"

    def __str__(self):
        return f"Patient {self.patient.full_name} ({self.patient_hospital_id}) - Hospital {self.hospital.name}"


class Episode(Model):
    class EpisodeChoices(TextChoices):
        INGUINAL = ("INGUINAL", "Inguinal Mesh Hernia Repair")
        INCISIONAL = ("INCISIONAL", "Incisional Mesh Hernia Repair")
        FEMORAL = ("FEMORAL", "Femoral Mesh Hernia Repair")
        HIATUS = ("HIATUS", "Hiatus Mesh Hernia Repair")
        UMBILICAL = (
            "UMBILICAL",
            "Umbilical/Periumbilicial Mesh Hernia Repair",
        )

    class CepodChoices(TextChoices):
        PLANNED = ("PLANNED", "Planned")
        EMERGENCY = ("EMERGENCY", "Emergency")

    class SideChoices(TextChoices):
        LEFT = ("LEFT", "Left")
        RIGHT = ("RIGHT", "Right")

    class OccurenceChoices(TextChoices):
        PRIMARY = ("PRIMARY", "Primary")
        RECURRENT = ("RECURRENT", "Recurrent")
        RERECURRENT = ("RERECURRENT", "Rerecurrent")

    class TypeChoices(TextChoices):
        DIRECT = ("DIRECT", "Direct")
        INDIRECT = ("INDIRECT", "Indirect")
        PANTALOON = ("PANTALOON", "Pantaloon")

    class ComplexityChoices(TextChoices):
        SIMPLE = ("SIMPLE", "Simple")
        INCARCERATED = ("INCARCERATED", "Incarcerated")
        OBSTRUCTED = ("OBSTRUCTED", "Obstructed")
        STRANGULATED = ("STRANGULATED", "Strangulated")

    class MeshTypeChoices(TextChoices):
        TNMHP = ("TNMHP", "TNMHP Mesh")
        KCMC = ("KCMC", "KCMC Generic Mesh")
        COMMERCIAL = ("COMMERCIAL", "Commercial Mesh")

    class AnaestheticChoices(TextChoices):
        LOCAL = ("LOCAL", "Local Anaesthetic")
        SPINAL = ("SPINAL", "Spinal Anaesthetic")
        GENERAL = ("GENERAL", "General Anaesthetic")

    patient_hospital_mapping = ForeignKey(
        PatientHospitalMapping, on_delete=CASCADE
    )
    created = DateTimeField(auto_now_add=True)
    surgery_date = DateField(null=True, blank=True)
    episode_type = CharField(max_length=128, choices=EpisodeChoices.choices)
    surgeons = ManyToManyField(MedicalPersonnel)
    comments = TextField(null=True, blank=True)
    cepod = CharField(max_length=16, choices=CepodChoices.choices)
    side = CharField(max_length=16, choices=SideChoices.choices)
    occurence = CharField(max_length=16, choices=OccurenceChoices.choices)
    type = CharField(max_length=16, choices=TypeChoices.choices)
    complexity = CharField(max_length=16, choices=ComplexityChoices.choices)
    mesh_type = CharField(max_length=16, choices=MeshTypeChoices.choices)
    anaesthetic_type = CharField(
        max_length=16, choices=AnaestheticChoices.choices
    )
    diathermy_used = BooleanField()

    def __str__(self):
        return f"({self.episode_type}) {self.patient_hospital_mapping.patient.full_name}"

    class Meta:
        verbose_name_plural = "Episodes"


class Discharge(TimeStampMixin):
    episode = OneToOneField(
        Episode, on_delete=CASCADE, related_name="discharge"
    )
    date = DateField()
    aware_of_mesh = BooleanField()
    infection = BooleanField()

    def __str__(self):
        return f"Episode {self.episode.id} Discharge {self.id} - {self.date}"

    class Meta:
        verbose_name_plural = "Discharges"


class FollowUp(Model):
    class PainSeverityChoices(TextChoices):
        NO_PAIN = ("NO_PAIN", "No Pain")
        MINIMAL = ("MINIMAL", "Minimal")
        MILD = ("MILD", "Mild")
        MODERATE = ("MODERATE", "Moderate")
        SEVERE = ("SEVERE", "Severe")

    episode = ForeignKey(Episode, on_delete=CASCADE)
    follow_up_date = DateField()
    pain_severity = CharField(
        max_length=16, choices=PainSeverityChoices.choices
    )
    attendees = ManyToManyField(MedicalPersonnel)
    mesh_awareness = BooleanField()
    seroma = BooleanField()
    infection = BooleanField()
    numbness = BooleanField()

    def __str__(self):
        return f"[{self.follow_up_date}] {self.episode}"

    class Meta:
        verbose_name_plural = "Follow Ups"
