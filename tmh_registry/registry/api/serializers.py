from rest_framework import serializers

from ..models import Hospital, Patient, PatientHospitalMapping


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ["id", "name", "address"]


class ReadPatientSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(allow_null=True)
    hospitals = serializers.SerializerMethodField()

    def get_hospitals(self, obj):
        hospitals = Hospital.objects.filter(
            id__in=PatientHospitalMapping.objects.filter(
                patient=obj
            ).values_list("hospital_id", flat=True)
        )
        return HospitalSerializer(hospitals, many=True).data

    class Meta:
        model = Patient
        fields = [
            "id",
            "full_name",
            "national_id",
            "age",
            "day_of_birth",
            "month_of_birth",
            "year_of_birth",
            "gender",
            "phone_1",
            "phone_2",
            "address",
            "hospitals",
        ]

    def to_representation(self, instance):
        data = super(ReadPatientSerializer, self).to_representation(instance)

        data["national_id"] = (
            int(data["national_id"]) if data["national_id"] else None
        )
        data["phone_1"] = int(data["phone_1"]) if data["phone_1"] else None
        data["phone_2"] = int(data["phone_2"]) if data["phone_2"] else None
        data["age"] = instance.age

        return data


class CreatePatientSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(allow_null=True)
    hospital_id = serializers.IntegerField(write_only=True)
    year_of_birth = serializers.IntegerField(allow_null=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "full_name",
            "national_id",
            "age",
            "day_of_birth",
            "month_of_birth",
            "year_of_birth",
            "gender",
            "phone_1",
            "phone_2",
            "address",
            "hospital_id",
        ]

    def to_representation(self, instance):
        serializer = ReadPatientSerializer(instance)
        return serializer.data

    def create(self, validated_data):

        if not validated_data.get("year_of_birth", None):
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

        if validated_data.get("hospital_id", None):
            try:
                hospital = Hospital.objects.get(
                    id=validated_data["hospital_id"]
                )
            except Hospital.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "error": "The hospital you are trying to register this patient does not exist."
                    }
                )
            validated_data.pop("hospital_id", None)
        else:
            raise serializers.ValidationError(
                {"error": "The patient needs to be registered to a hospital."}
            )

        validated_data.pop("age", None)
        new_patient = super(CreatePatientSerializer, self).create(
            validated_data
        )
        PatientHospitalMapping.objects.create(
            patient=new_patient, hospital=hospital
        )

        return new_patient