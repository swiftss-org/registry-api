from rest_framework import serializers

from ..models import Hospital, Patient


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ["id", "name", "address"]


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "id",
            "first_name",
            "last_name",
            "national_id",
            "age",
            "day_of_birth",
            "month_of_birth",
            "year_of_birth",
            "gender",
            "phone_1",
            "phone_2",
            "address",
        ]
