from django.contrib import admin

from tmh_registry.registry.models import (
    Episode,
    Hospital,
    Patient,
    PatientHospitalMapping, Discharge, FollowUp,
)

@admin.register(Discharge)
class DischargeAdmin(admin.ModelAdmin):
    model = Discharge

@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    model = FollowUp

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    model = Hospital


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    model = Patient


@admin.register(PatientHospitalMapping)
class PatientHospitalMappingAdmin(admin.ModelAdmin):
    model = PatientHospitalMapping


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    model = Episode
