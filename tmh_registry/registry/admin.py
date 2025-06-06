from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from import_export import resources
from import_export.admin import ExportMixin

from tmh_registry.registry.models import (
    Discharge,
    Episode,
    FollowUp,
    Hospital,
    Patient,
    PatientHospitalMapping,
    PreferredHospital,
    Zone,
    Region,
    HospitalRegionMapping,
    RegionZoneMapping, Announcement,
)


@admin.register(Discharge)
class DischargeAdmin(ExportMixin, admin.ModelAdmin):
    model = Discharge


@admin.register(FollowUp)
class FollowUpAdmin(ExportMixin, admin.ModelAdmin):
    model = FollowUp


@admin.register(Hospital)
class HospitalAdmin(ExportMixin, admin.ModelAdmin):
    model = Hospital


@admin.register(Patient)
class PatientAdmin(ExportMixin, admin.ModelAdmin):
    model = Patient


@admin.register(PatientHospitalMapping)
class PatientHospitalMappingAdmin(ExportMixin, admin.ModelAdmin):
    model = PatientHospitalMapping

@admin.register(PreferredHospital)
class PreferredHospitalAdmin(ExportMixin, admin.ModelAdmin):
    model = PreferredHospital

@admin.register(Episode)
class EpisodeAdmin(ExportMixin, admin.ModelAdmin):
    model = Episode

@admin.register(Zone)
class ZoneAdmin(ExportMixin, admin.ModelAdmin):
    model = Zone

@admin.register(Region)
class RegionAdmin(ExportMixin, admin.ModelAdmin):
    model = Region

@admin.register(HospitalRegionMapping)
class HospitalRegionMappingAdmin(ExportMixin, admin.ModelAdmin):
    model = HospitalRegionMapping

@admin.register(RegionZoneMapping)
class RegionZoneMappingAdmin(ExportMixin, admin.ModelAdmin):
    model = RegionZoneMapping

@admin.register(Announcement)
class AnnouncementAdmin(ExportMixin, admin.ModelAdmin):
    model = Announcement
"""
To allow CSV export on User model
"""


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class UserAdmin(ExportMixin, UserAdmin):
    resource_class = UserResource


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
