from django.contrib import admin

from tmh_registry.registry.models import (
    Hospital,
    Patient,
    PatientHospitalMapping,
)
from tmh_registry.users.models import MedicalPersonnel


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    model = Hospital


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    model = Patient


@admin.register(MedicalPersonnel)
class MedicalPersonnelAdmin(admin.ModelAdmin):
    model = MedicalPersonnel


@admin.register(PatientHospitalMapping)
class PatientHospitalMappingAdmin(admin.ModelAdmin):
    model = PatientHospitalMapping
