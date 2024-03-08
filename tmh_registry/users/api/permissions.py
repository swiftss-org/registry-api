from rest_framework import permissions

from tmh_registry.users.models import MedicalPersonnel

import traceback
import logging


class IsMedicalPersonnel(permissions.BasePermission):
    message = "MedicalPersonnel instance is required"

    def has_permission(self, request, view):
        try:
            return request.user.medical_personnel.user.is_staff
        except MedicalPersonnel.DoesNotExist:
            return False
        except Exception:
            return False

