from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from ..models import Hospital, Patient, PatientHospitalMapping


class HospitalSerializer(ModelSerializer):
    class Meta:
        model = Hospital
        fields = ["id", "name", "address"]


class PatientHospitalMappingPatientSerializer(ModelSerializer):
    class Meta:
        model = PatientHospitalMapping
        fields = ["patient_hospital_id", "hospital_id"]


class ReadPatientSerializer(ModelSerializer):
    age = IntegerField(allow_null=True)
    hospital_mappings = PatientHospitalMappingPatientSerializer(many=True)

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
            "hospital_mappings",
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


class CreatePatientSerializer(ModelSerializer):
    age = IntegerField(allow_null=True)
    hospital_id = IntegerField(write_only=True)
    patient_hospital_id = IntegerField(write_only=True)
    year_of_birth = IntegerField(allow_null=True)

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
            "patient_hospital_id",
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
                raise ValidationError(
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
                raise ValidationError(
                    {
                        "error": "The hospital you are trying to register this patient does not exist."
                    }
                )
            validated_data.pop("hospital_id", None)
        else:
            raise ValidationError(
                {"error": "The patient needs to be registered to a hospital."}
            )

        patient_hospital_id = validated_data.pop("patient_hospital_id", None)
        if patient_hospital_id:
            if PatientHospitalMapping.objects.filter(
                hospital_id=hospital.id,
                patient_hospital_id=patient_hospital_id,
            ).exists():
                raise ValidationError(
                    {
                        "error": f"The patient hospital id {patient_hospital_id} is already "
                        f"registered to another patient of this hospital."
                    }
                )
        else:
            raise ValidationError(
                {"error": "The patient needs to be registered to a hospital."}
            )

        validated_data.pop("age", None)
        new_patient = super(CreatePatientSerializer, self).create(
            validated_data
        )
        PatientHospitalMapping.objects.create(
            patient=new_patient,
            hospital=hospital,
            patient_hospital_id=patient_hospital_id,
        )

        return new_patient


class PatientHospitalMappingReadSerializer(ModelSerializer):
    patient = ReadPatientSerializer()
    hospital = HospitalSerializer()

    class Meta:
        model = PatientHospitalMapping
        fields = ["patient", "hospital", "patient_hospital"]


class PatientHospitalMappingWriteSerializer(ModelSerializer):
    patient_id = PrimaryKeyRelatedField(queryset=Patient.objects.all())
    hospital_id = PrimaryKeyRelatedField(queryset=Hospital.objects.all())

    class Meta:
        model = PatientHospitalMapping
        fields = ["patient_id", "hospital_id", "patient_hospital_id"]

    def create(self, validated_data):
        validated_data["patient_id"] = validated_data["patient_id"].id
        validated_data["hospital_id"] = validated_data["hospital_id"].id

        existing_mapping = PatientHospitalMapping.objects.filter(
            patient_id=validated_data["patient_id"],
            hospital_id=validated_data["hospital_id"],
        )
        if existing_mapping.exists():
            raise ValidationError(
                {
                    "error": "PatientHospitalMapping for patient_id {patient_id} and hospital_id {hospital_id} "
                    "already exists!".format(
                        patient_id=validated_data["patient_id"],
                        hospital_id=validated_data["hospital_id"],
                    )
                }
            )

        existing_patient_hospital_id = PatientHospitalMapping.objects.filter(
            patient_hospital_id=validated_data["patient_hospital_id"],
            hospital_id=validated_data["hospital_id"],
        )
        if existing_patient_hospital_id.exists():
            raise ValidationError(
                {
                    "error": "Patient Hospital ID {patient_hospital_id} already exists for another patient in "
                    "this hospital".format(
                        patient_hospital_id=validated_data[
                            "patient_hospital_id"
                        ]
                    )
                }
            )

        new_mapping = PatientHospitalMapping.objects.create(
            patient_hospital_id=validated_data["patient_hospital_id"],
            hospital_id=validated_data["hospital_id"],
            patient_id=validated_data["patient_id"],
        )

        return new_mapping
