from django.contrib import admin

from tmh_registry.registry.models import (
    Hospital,
    Patient,
    PatientHospitalMapping,
)


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    model = Hospital


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    model = Patient


@admin.register(PatientHospitalMapping)
class PatientHospitalMappingAdmin(admin.ModelAdmin):
    model = PatientHospitalMapping
