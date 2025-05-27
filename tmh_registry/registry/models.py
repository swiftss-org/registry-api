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
        MALE = ("MALE", "Male")
        FEMALE = ("FEMALE", "Female")

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
        verbose_name_plural = "Patient-Hospital Mappings"

    def __str__(self):
        return f"Patient {self.patient.full_name} ({self.patient_hospital_id}) - Hospital {self.hospital.name}"

class PreferredHospital(Model):
    medical_personnel = OneToOneField(
        MedicalPersonnel, on_delete=CASCADE, related_name="preferred_hospital"
    )
    hospital = ForeignKey(
        Hospital, on_delete=CASCADE, related_name="preferred_by_medical_personnel"
    )

    class Meta:
        unique_together = (
            ("medical_personnel", "hospital"),
        )
        verbose_name_plural = "Medical Personnel Preferred Hospitals"

    def __str__(self):
        return f"{self.medical_personnel.user.first_name} {self.medical_personnel.user.last_name} ({self.medical_personnel.user.username}) - Hospital {self.hospital.name}"

class Episode(Model):
    class EpisodeChoices(TextChoices):
        INGUINAL = ("INGUINAL", "Inguinal Mesh Hernia Repair")
        INCISIONAL = ("INCISIONAL", "Incisional Mesh Hernia Repair")
        FEMORAL = ("FEMORAL", "Femoral Mesh Hernia Repair")
        UMBILICAL = (
            "UMBILICAL",
            "Umbilical/Periumbilicial Mesh Hernia Repair",
        )
        EPIGASTRIC = ("EPIGASTRIC", "Epigastric Hernia")

    class CepodChoices(TextChoices):
        PLANNED = ("PLANNED", "Planned")
        EMERGENCY = ("EMERGENCY", "Emergency")

    class SideChoices(TextChoices):
        NA = ("NA", "Not Applicable")
        LEFT = ("LEFT", "Left")
        RIGHT = ("RIGHT", "Right")

    class OccurenceChoices(TextChoices):
        PRIMARY = ("PRIMARY", "Primary")
        RECURRENT = ("RECURRENT", "Recurrent")
        RERECURRENT = ("RERECURRENT", "Rerecurrent")

    class TypeChoices(TextChoices):
        NA = ("NA", "Not Applicable")
        DIRECT = ("DIRECT", "Direct")
        INDIRECT = ("INDIRECT", "Indirect")
        PANTALOON = ("PANTALOON", "Pantaloon")

    class SizeChoices(TextChoices):
        VERY_SMALL = ("VERY_SMALL", "Very Small (<1 finger breadth)")
        SMALL = ("SMALL", "Small (1-2 finger breadths)")
        MEDIUM = ("MEDIUM", "Medium (2-3 finger breadths)")
        LARGE = ("LARGE", "Large (3-4 finger breadths)")
        VERY_LARGE = ("VERY_LARGE", "Very Large (>4 finger breadths)")
        MASSIVE = ("MASSIVE", "Massive (extends beyond midpoint of thigh)")

    class ComplexityChoices(TextChoices):
        SIMPLE = ("SIMPLE", "Simple")
        INCARCERATED = ("INCARCERATED", "Irreducible")
        OBSTRUCTED = ("OBSTRUCTED", "With bowel obstruction")
        STRANGULATED = ("STRANGULATED", "Strangulated")

    class MeshTypeChoices(TextChoices):
        TNMHP = ("TNMHP", "TNMHP Mesh")
        KCMC = ("KCMC", "KCMC Generic Mesh")
        COMMERCIAL = ("COMMERCIAL", "Commercial Mesh")
        INTERNATIONAL = ("INTERNATIONAL", "Hernia International Mesh")

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
    cepod = CharField(max_length=16, choices=CepodChoices.choices)
    side = CharField(max_length=16, choices=SideChoices.choices)
    occurence = CharField(max_length=16, choices=OccurenceChoices.choices)
    type = CharField(max_length=16, choices=TypeChoices.choices)
    size = CharField(max_length=16, choices=SizeChoices.choices)
    complexity = CharField(max_length=16, choices=ComplexityChoices.choices)
    mesh_type = CharField(max_length=16, choices=MeshTypeChoices.choices)
    anaesthetic_type = CharField(
        max_length=16, choices=AnaestheticChoices.choices
    )
    diathermy_used = BooleanField()
    antibiotic_used = BooleanField()
    antibiotic_type = CharField(max_length=128, null=True, blank=True)
    comments = TextField(null=True, blank=True)

    def __str__(self):
        return f"({self.episode_type}) {self.patient_hospital_mapping.patient.full_name}"

    class Meta:
        verbose_name_plural = "Episodes"


class Discharge(TimeStampMixin):
    episode = OneToOneField(
        Episode, on_delete=CASCADE, related_name="discharge"
    )
    date = DateField()
    aware_of_mesh = BooleanField()  # antibiotics given on discharge
    infection = CharField(
        max_length=64, null=True, blank=True
    )  # Post-operative complications (comma separated values)
    discharge_duration = PositiveIntegerField(null=True, blank=True)
    comments = TextField(null=True, blank=True)

    def __str__(self):
        return f"Episode {self.episode} | Discharge {self.id} - {self.date}"

    class Meta:
        verbose_name_plural = "Discharges"


class FollowUp(TimeStampMixin):
    class PainSeverityChoices(TextChoices):
        NO_PAIN = ("NO_PAIN", "No Pain")
        MINIMAL = ("MINIMAL", "Minimal")
        MILD = ("MILD", "Mild")
        MODERATE = ("MODERATE", "Moderate")
        SEVERE = ("SEVERE", "Severe")

    episode = ForeignKey(Episode, on_delete=CASCADE)
    date = DateField()
    pain_severity = CharField(
        max_length=16, choices=PainSeverityChoices.choices
    )
    attendees = ManyToManyField(MedicalPersonnel)
    mesh_awareness = BooleanField()
    seroma = BooleanField()
    infection = BooleanField()
    numbness = BooleanField()
    recurrence = BooleanField(null=True, blank=False)
    further_surgery_need = BooleanField()
    surgery_comments_box = TextField(null=True, blank=True)

    def __str__(self):
        return f"Episode {self.episode} | FollowUp {self.id} - {self.date}"

    class Meta:
        verbose_name_plural = "Follow Ups"

class Zone(Model):
    name = CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Zones"

class Region(Model):
    name = CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Regions"

class HospitalRegionMapping(Model):
    hospital = OneToOneField(
        Hospital,
        on_delete=CASCADE,
        related_name="region_mapping"
    )
    region = ForeignKey(
        Region,
        on_delete=CASCADE,
        related_name="hospital_mappings"
    )
    def __str__(self):
        return f"{self.hospital.name} - {self.region.name}"
    class Meta:
        verbose_name_plural = "Hospital-Region Mappings"

class RegionZoneMapping(Model):
    region = OneToOneField(
        Region,
        on_delete=CASCADE,
        related_name="zone_mapping"
    )
    zone = ForeignKey(
        Zone,
        on_delete=CASCADE,
        related_name="region_mappings"
    )
    def __str__(self):
        return f"{self.region.name} - {self.zone.name}"
    class Meta:
        verbose_name_plural = "Region-Zone Mappings"

class Announcement(Model):
    announcement_text = TextField()
    display_from = DateTimeField(null=True, blank=True)
    display_until = DateTimeField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Announcement ({self.created_at}): {self.announcement_text[:50]}"
