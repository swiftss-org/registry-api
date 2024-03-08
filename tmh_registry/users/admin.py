from django.contrib import admin
from import_export.admin import ExportMixin

from tmh_registry.users.models import MedicalPersonnel


@admin.register(MedicalPersonnel)
class MedicalPersonnelAdmin(ExportMixin, admin.ModelAdmin):
    model = MedicalPersonnel
