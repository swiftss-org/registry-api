from drf_yasg.utils import swagger_serializer_method
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, IntegerField, BooleanField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from ...common.utils.functions import get_text_choice_value_from_label
from ...users.api.serializers import MedicalPersonnelSerializer
from ...users.models import MedicalPersonnel
from ..models import (
    Discharge,
    Episode,
    FollowUp,
    Hospital,
    Patient,
    PatientHospitalMapping,
)


class HospitalSerializer(ModelSerializer):
    class Meta:
        model = Hospital
        fields = ["id", "name", "address"]


class EpisodeSerializer(ModelSerializer):
    surgeons = MedicalPersonnelSerializer(many=True)
    episode_type = CharField(source="get_episode_type_display")
    cepod = CharField(source="get_cepod_display")
    side = CharField(source="get_side_display")
    occurence = CharField(source="get_occurence_display")
    type = CharField(source="get_type_display")
    size = CharField(source="get_size_display")
    complexity = CharField(source="get_complexity_display")
    mesh_type = CharField(source="get_mesh_type_display")
    anaesthetic_type = CharField(source="get_anaesthetic_type_display")

    class Meta:
        model = Episode
        fields = [
            "id",
            "surgery_date",
            "episode_type",
            "surgeons",
            "comments",
            "cepod",
            "side",
            "occurence",
            "type",
            "size",
            "complexity",
            "mesh_type",
            "anaesthetic_type",
            "diathermy_used",
            "antibiotic_used",
            "antibiotic_type",
        ]


class PatientHospitalMappingPatientSerializer(ModelSerializer):
    class Meta:
        model = PatientHospitalMapping
        fields = ["patient_hospital_id", "hospital_id"]

    def to_representation(self, instance):
        data = super(
            PatientHospitalMappingPatientSerializer, self
        ).to_representation(instance)

        return data


class ReadPatientSerializer(ModelSerializer):
    age = IntegerField(allow_null=True)
    hospital_mappings = PatientHospitalMappingPatientSerializer(many=True)
    episodes = SerializerMethodField()
    gender = CharField(source="get_gender_display")

    @swagger_serializer_method(serializer_or_field=EpisodeSerializer)
    def get_episodes(self, obj):
        episodes = Episode.objects.filter(
            patient_hospital_mapping__patient__id__in=obj.hospital_mappings.values_list(
                "patient_id", flat=True
            )
        )
        return EpisodeSerializer(episodes, many=True).data

    class Meta:
        model = Patient
        fields = [
            "id",
            "full_name",
            "created_at",
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
            "episodes",
        ]

    def to_representation(self, instance):
        data = super(ReadPatientSerializer, self).to_representation(instance)

        # data["national_id"] = (
        #     int(data["national_id"]) if data["national_id"] else None
        # )
        # data["phone_1"] = int(data["phone_1"]) if data["phone_1"] else None
        # data["phone_2"] = int(data["phone_2"]) if data["phone_2"] else None
        data["age"] = instance.age
        return data


class CreatePatientSerializer(ModelSerializer):
    age = IntegerField(allow_null=True)
    hospital_id = IntegerField(write_only=True)
    patient_hospital_id = CharField(write_only=True)
    day_of_birth = IntegerField(allow_null=True, required=False)
    month_of_birth = IntegerField(allow_null=True, required=False)
    year_of_birth = IntegerField(allow_null=True)
    gender = CharField(allow_null=True)
    phone_1 = CharField(allow_null=True)

    class Meta:
        model = Patient
        fields = [
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

        patient_hospital_id = validated_data.pop("patient_hospital_id")

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
                {"error": "The 'patient_hospital_id' should be provided."}
            )

        validated_data["gender"] = (
            get_text_choice_value_from_label(
                Patient.Gender.choices, validated_data["gender"]
            )
            if validated_data["gender"]
            else validated_data["gender"]
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
        fields = ["patient", "hospital", "patient_hospital_id"]

    def to_representation(self, instance):
        data = super(
            PatientHospitalMappingReadSerializer, self
        ).to_representation(instance)

        data["patient_hospital_id"] = (
            int(data["patient_hospital_id"])
            if data["patient_hospital_id"]
            else None
        )

        return data


class PatientHospitalMappingWriteSerializer(ModelSerializer):
    patient_id = PrimaryKeyRelatedField(queryset=Patient.objects.all())
    hospital_id = PrimaryKeyRelatedField(queryset=Hospital.objects.all())

    class Meta:
        model = PatientHospitalMapping
        fields = ["patient_id", "hospital_id", "patient_hospital_id"]

    def to_representation(self, instance):
        serializer = PatientHospitalMappingReadSerializer(instance)
        return serializer.data

    def create(self, validated_data):
        try:
            validated_data["patient_hospital_id"] = int(
                validated_data.get("patient_hospital_id")
            )
        except ValueError:
            raise ValidationError(
                {
                    "error": "The 'patient_hospital_id' field should be an integer."
                }
            )
        validated_data["patient_hospital_id"] = str(
            validated_data["patient_hospital_id"]
        )
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


class EpisodeReadSerializer(ModelSerializer):
    patient_hospital_mapping = PatientHospitalMappingReadSerializer()
    surgeons = MedicalPersonnelSerializer(many=True)
    episode_type = CharField(source="get_episode_type_display")
    cepod = CharField(source="get_cepod_display")
    side = CharField(source="get_side_display")
    occurence = CharField(source="get_occurence_display")
    type = CharField(source="get_type_display")
    size = CharField(source="get_size_display")
    complexity = CharField(source="get_complexity_display")
    mesh_type = CharField(source="get_mesh_type_display")
    anaesthetic_type = CharField(source="get_anaesthetic_type_display")
    antibiotic_type = CharField()

    class Meta:
        model = Episode
        fields = [
            "id",
            "patient_hospital_mapping",
            "created",
            "surgery_date",
            "episode_type",
            "surgeons",
            "comments",
            "cepod",
            "side",
            "occurence",
            "type",
            "size",
            "complexity",
            "mesh_type",
            "anaesthetic_type",
            "diathermy_used",
            "antibiotic_used",
            "antibiotic_type",
        ]


class EpisodeWriteSerializer(ModelSerializer):
    patient_id = PrimaryKeyRelatedField(
        write_only=True, queryset=Patient.objects.all()
    )
    hospital_id = PrimaryKeyRelatedField(
        write_only=True, queryset=Hospital.objects.all()
    )
    surgeon_ids = PrimaryKeyRelatedField(
        write_only=True, many=True, queryset=MedicalPersonnel.objects.all()
    )
    episode_type = CharField()
    comments = CharField(required=False)
    cepod = CharField()
    side = CharField()
    occurence = CharField()
    type = CharField()
    size = CharField()
    complexity = CharField()
    mesh_type = CharField()
    anaesthetic_type = CharField()
    antibiotic_type = CharField(required=False)

    class Meta:
        model = Episode
        fields = [
            "patient_id",
            "hospital_id",
            "surgery_date",
            "episode_type",
            "surgeon_ids",
            "comments",
            "cepod",
            "side",
            "occurence",
            "type",
            "size",
            "complexity",
            "mesh_type",
            "anaesthetic_type",
            "diathermy_used",
            "antibiotic_used",
            "antibiotic_type",
        ]

    def to_representation(self, instance):
        serializer = EpisodeReadSerializer(instance)
        return serializer.data

    def create(self, validated_data):
        patient = validated_data["patient_id"]
        hospital = validated_data["hospital_id"]
        surgeons = validated_data["surgeon_ids"]

        patient_hospital_mapping = PatientHospitalMapping.objects.filter(
            patient_id=patient.id,
            hospital_id=hospital.id,
        ).first()
        if patient_hospital_mapping is None:
            raise ValidationError(
                {
                    "error": "PatientHospitalMapping for patient_id {patient_id} and hospital_id {hospital_id} "
                    "does not exist.".format(
                        patient_id=patient.id,
                        hospital_id=hospital.id,
                    )
                }
            )

        try:
            episode = Episode.objects.create(
                patient_hospital_mapping=patient_hospital_mapping,
                surgery_date=validated_data["surgery_date"],
                episode_type=get_text_choice_value_from_label(
                    Episode.EpisodeChoices.choices,
                    validated_data["episode_type"],
                ),
                comments=validated_data.get("comments", ""),
                cepod=get_text_choice_value_from_label(
                    Episode.CepodChoices.choices, validated_data["cepod"]
                ),
                side=get_text_choice_value_from_label(
                    Episode.SideChoices.choices, validated_data["side"]
                ),
                occurence=get_text_choice_value_from_label(
                    Episode.OccurenceChoices.choices,
                    validated_data["occurence"],
                ),
                type=get_text_choice_value_from_label(
                    Episode.TypeChoices.choices, validated_data["type"]
                ),
                size=get_text_choice_value_from_label(
                    Episode.SizeChoices.choices, validated_data["size"]
                ),
                complexity=get_text_choice_value_from_label(
                    Episode.ComplexityChoices.choices,
                    validated_data["complexity"],
                ),
                mesh_type=get_text_choice_value_from_label(
                    Episode.MeshTypeChoices.choices,
                    validated_data["mesh_type"],
                ),
                anaesthetic_type=get_text_choice_value_from_label(
                    Episode.AnaestheticChoices.choices,
                    validated_data["anaesthetic_type"],
                ),
                diathermy_used=validated_data["diathermy_used"],
                antibiotic_used=validated_data["antibiotic_used"],
                antibiotic_type=validated_data.get("antibiotic_type", "")
            )
        except IndexError:
            raise ValidationError(
                {"error": "Not supported value provided for ChoiceField."}
            )

        if surgeons:
            episode.surgeons.set(surgeons)

        return episode


class DischargeReadSerializer(ModelSerializer):
    episode = EpisodeReadSerializer()

    class Meta:
        model = Discharge
        fields = [
            "id",
            "episode",
            "date",
            "aware_of_mesh",
            "infection",
            "discharge_duration",
            "comments"
        ]


class DischargeWriteSerializer(ModelSerializer):
    episode_id = PrimaryKeyRelatedField(
        write_only=True, queryset=Episode.objects.filter(discharge=None)
    )
    comments = CharField(required=False, allow_null=True, allow_blank=True)
    infection = CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Discharge
        fields = [
            "episode_id",
            "date",
            "aware_of_mesh",
            "infection",
            "discharge_duration",
            "comments"
        ]

    def to_representation(self, instance):
        serializer = DischargeReadSerializer(instance)
        return serializer.data

    def create(self, validated_data):
        episode = validated_data["episode_id"]

        if episode.surgery_date > validated_data["date"]:
            raise ValidationError(
                {
                    "error": "Episode surgery date cannot be after Discharge date"
                }
            )

        discharge = Discharge.objects.create(
            episode_id=episode.id,
            date=validated_data["date"],
            aware_of_mesh=validated_data["aware_of_mesh"],
            infection=validated_data.get("infection", ""),
            discharge_duration=validated_data.get("discharge_duration", ""),
            comments=validated_data.get("comments", "")
        )

        return discharge


class FollowUpReadSerializer(ModelSerializer):
    episode = EpisodeReadSerializer()
    pain_severity = CharField(source="get_pain_severity_display")
    attendees = MedicalPersonnelSerializer(many=True)

    class Meta:
        model = FollowUp
        fields = [
            "id",
            "episode",
            "date",
            "pain_severity",
            "attendees",
            "mesh_awareness",
            "seroma",
            "infection",
            "numbness",
            "further_surgery_need",
            "surgery_comments_box"
        ]


class FollowUpWriteSerializer(ModelSerializer):
    episode_id = PrimaryKeyRelatedField(
        write_only=True, queryset=Episode.objects.exclude(discharge=None)
    )
    attendee_ids = PrimaryKeyRelatedField(
        write_only=True, many=True, queryset=MedicalPersonnel.objects.all()
    )
    pain_severity = CharField()
    surgery_comments_box = CharField(required=False, allow_blank=True, allow_null=True)
    further_surgery_need = BooleanField()

    class Meta:
        model = FollowUp
        fields = [
            "episode_id",
            "date",
            "pain_severity",
            "attendee_ids",
            "mesh_awareness",
            "seroma",
            "infection",
            "numbness",
            "further_surgery_need",
            "surgery_comments_box"
        ]

    def to_representation(self, instance):
        serializer = FollowUpReadSerializer(instance)
        return serializer.data

    def create(self, validated_data):
        episode = validated_data["episode_id"]
        attendees = validated_data["attendee_ids"]

        if episode.surgery_date > validated_data["date"]:
            raise ValidationError(
                {
                    "error": "Episode surgery date cannot be after Follow Up date"
                }
            )

        if episode.discharge.date > validated_data["date"]:
            raise ValidationError(
                {
                    "error": "Episode Discharge date cannot be after Follow Up date"
                }
            )

        pain_severity = validated_data.get("pain_severity", "")
        print(f"{pain_severity=}")
        follow_up = FollowUp.objects.create(
            episode_id=episode.id,
            date=validated_data["date"],
            pain_severity=get_text_choice_value_from_label(
                FollowUp.PainSeverityChoices.choices, pain_severity
            )
            if pain_severity
            else "",
            mesh_awareness=validated_data["mesh_awareness"],
            seroma=validated_data["seroma"],
            infection=validated_data["infection"],
            numbness=validated_data["numbness"],
            further_surgery_need=validated_data["further_surgery_need"],
            surgery_comments_box=validated_data.get("surgery_comments_box", "")
        )

        follow_up.attendees.set(attendees)

        return follow_up
