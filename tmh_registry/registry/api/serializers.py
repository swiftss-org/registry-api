from rest_framework import serializers

from ..models import Hospital, Patient


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ["id", "name", "address"]


class PatientSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(allow_null=True)

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

    def to_representation(self, instance):
        data = super(PatientSerializer, self).to_representation(instance)

        data["national_id"] = int(data["national_id"])
        data["phone_1"] = int(data["phone_1"])
        data["phone_2"] = int(data["phone_2"])
        data["age"] = instance.age

        return data

    def create(self, validated_data):

        if not validated_data["year_of_birth"]:
            if validated_data["age"]:
                validated_data[
                    "year_of_birth"
                ] = Patient.get_year_of_birth_from_age(validated_data["age"])
            else:
                raise serializers.ValidationError(
                    {
                        "error": "Either 'age' or 'year_of_birth' should be populated."
                    }
                )

        validated_data.pop("age", None)

        return super(PatientSerializer, self).create(validated_data)
