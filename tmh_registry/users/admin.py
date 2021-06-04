from django.contrib import admin

from tmh_registry.users.models import MedicalPersonnel


@admin.register(MedicalPersonnel)
class MedicalPersonnelAdmin(admin.ModelAdmin):
    model = MedicalPersonnel
    list_display = ("__all__",)
