from django.core.exceptions import ObjectDoesNotExist
from django.db.models import CharField, Q, Count, Max, OuterRef, Exists
from django.db.models.functions import Cast
from django.utils.decorators import method_decorator
from django_filters import (  # pylint: disable=E0401
    CharFilter,
    NumberFilter,
    OrderingFilter,
)
from django_filters.rest_framework import FilterSet  # pylint: disable=E0401
from drf_yasg import openapi
from drf_yasg.openapi import IN_QUERY, TYPE_INTEGER, TYPE_STRING, Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from django.utils.timezone import now

from ..models import (
    Discharge,
    Episode,
    FollowUp,
    Hospital,
    Patient,
    PatientHospitalMapping,
    PreferredHospital,
    Announcement,
)
from .serializers import (
    CreatePatientSerializer,
    DischargeReadSerializer,
    DischargeWriteSerializer,
    EpisodeReadSerializer,
    EpisodeWriteSerializer,
    FollowUpReadSerializer,
    FollowUpWriteSerializer,
    HospitalSerializer,
    PatientHospitalMappingReadSerializer,
    PatientHospitalMappingWriteSerializer,
    PreferredHospitalReadSerializer,
    ReadPatientSerializer,
    SurgeonEpisodeSummarySerializer, OwnedEpisodeSerializer, UnlinkedPatientSerializer, AnnouncementSerializer,
)
from ...users.models import MedicalPersonnel


class HospitalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer

class PreferredHospitalViewSet(viewsets.GenericViewSet):
    serializer_class = PreferredHospitalReadSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def retrieve_for_current_user(self, request, *args, **kwargs):
        user = request.user
        try:
            medical_personnel = MedicalPersonnel.objects.get(user=user)
        except MedicalPersonnel.DoesNotExist:
            return Response({}, status=200)
        try:
            preferred_hospital = PreferredHospital.objects.get(medical_personnel=medical_personnel)
        except PreferredHospital.DoesNotExist:
            return Response({}, status=200)
        serializer = self.get_serializer(preferred_hospital)
        return Response(serializer.data)

class SurgeonEpisodeSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SurgeonEpisodeSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            medical_personnel = MedicalPersonnel.objects.get(user=user)
        except MedicalPersonnel.DoesNotExist:
            return Episode.objects.none()

        return Episode.objects.filter(surgeons=medical_personnel)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        stats = queryset.aggregate(
            episode_count=Count('id'),
            last_episode_date=Max('surgery_date')
        )

        serializer = self.get_serializer(stats)
        return Response(serializer.data)

class OwnedEpisodesViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = OwnedEpisodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            medical_personnel = MedicalPersonnel.objects.get(user=user)
        except MedicalPersonnel.DoesNotExist:
            return Episode.objects.none()

        episodes = (
            Episode.objects
            .filter(surgeons=medical_personnel)
            .select_related("patient_hospital_mapping__patient")
            .prefetch_related( "discharge", "followup_set")
        )
        return episodes

class PatientFilterSet(FilterSet):
    hospital_id = NumberFilter(
        method="filter_hospital",
        label="Filter based on hospital",
    )
    search_term = CharFilter(
        method="filter_search_term",
        label="Filter based on search_term",
    )
    ordering = OrderingFilter(
        fields=("full_name", "created_at"),
    )

    def filter_hospital(self, queryset, name, value):
        if value:
            patient_ids = PatientHospitalMapping.objects.filter(
                hospital_id=value
            ).values_list("patient_id", flat=True)
            queryset = queryset.filter(id__in=patient_ids)
        return queryset

    def filter_search_term(self, queryset, name, value):
        selected_hospital_id_value = self.data.get("hospital_id")
        if value:
            patient_ids = (
                PatientHospitalMapping.objects.annotate(
                    patient_hospital_id_str=Cast(
                        "patient_hospital_id", CharField()
                    )
                )
                .filter(
                    Q(patient_hospital_id_str__contains=str(value))
                    & Q(hospital_id=selected_hospital_id_value)
                )
                .values_list("patient_id", flat=True)
            )
            # pylint: disable=unsupported-binary-operation
            queryset = queryset.filter(
                Q(full_name__icontains=value)
                | Q(national_id__icontains=value)
                | Q(id__in=patient_ids)
                # pylint: enable=unsupported-binary-operation
            )
            return queryset
        return queryset

    class Meta:
        model = Patient
        fields = ["hospital_id", "search_term"]


@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Register a Patient",
        operation_description="Use this endpoint to register a patient. A PatientHospitalMapping will be created "
        "automatically for the newly created Patient and the provided Hospital.\n "
        f"\nAccepted values for `gender` are `{Patient.Gender.labels}`. \n ",
        responses={201: ReadPatientSerializer(many=True)},
    ),
)
@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            Parameter(
                "ordering",
                IN_QUERY,
                description="Choose with which field you want to order with. You can change to descending order by "
                "adding a `-` before the field name e.g. `ordering=-full_name`. "
                "Possible options: `[full_name, created_at]`",
                type=TYPE_STRING,
            ),
            Parameter(
                "hospital_id",
                IN_QUERY,
                description="Filter with patients of a specific hospital.",
                type=TYPE_INTEGER,
            ),
            Parameter(
                "search_term",
                IN_QUERY,
                description="Filter patients with search term. A patient will be returned if national id is an exact "
                "match or full name is even partially matched.",
                type=TYPE_INTEGER,
            ),
        ],
        responses={200: ReadPatientSerializer()},
    ),
)
class PatientViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    filterset_class = PatientFilterSet
    queryset = Patient.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ReadPatientSerializer
        if self.action == "create":
            return CreatePatientSerializer

        raise NotImplementedError


@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        responses={201: PatientHospitalMappingReadSerializer()}
    ),
)
class PatientHospitalMappingViewset(CreateModelMixin, GenericViewSet):
    queryset = PatientHospitalMapping.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return PatientHospitalMappingReadSerializer
        if self.action == "create":
            return PatientHospitalMappingWriteSerializer

        raise NotImplementedError


@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Register an Episode",
        operation_description="Use this endpoint to register an episode. Keep in mind that you need to create a "
        "`PatientHospitalMapping`(through the POST /patient-hospital-mappings/ endpoint) "
        "if one does not already exist for this specific Patient/Hospital pair.\n "
        f"\nAccepted values for `episode_type` are `{Episode.EpisodeChoices.labels}`. \n "
        f"\nAccepted values for `cepod` are `{Episode.CepodChoices.labels}`. \n "
        f"\nAccepted values for `side` are `{Episode.SideChoices.labels}`. \n "
        f"\nAccepted values for `occurence` are `{Episode.OccurenceChoices.labels}`. \n "
        f"\nAccepted values for `type` are `{Episode.TypeChoices.labels}`. \n "
        f"\nAccepted values for `size` are `{Episode.SizeChoices.labels}`. \n "
        f"\nAccepted values for `complexity` are `{Episode.ComplexityChoices.labels}`. \n "
        f"\nAccepted values for `mesh_type` are `{Episode.MeshTypeChoices.labels}`. \n "
        f"\nAccepted values for `anaesthetic_type` are `{Episode.AnaestheticChoices.labels}`. \n ",
        responses={201: EpisodeReadSerializer()},
    ),
)
class EpisodeViewset(CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Episode.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return EpisodeReadSerializer
        if self.action == "create":
            return EpisodeWriteSerializer

        raise NotImplementedError

    @swagger_auto_schema(
        method="get",
        responses={
            200: openapi.Response(
                "Returns a `Discharge` object.",
                DischargeReadSerializer,
            ),
        },
    )
    @action(
        detail=True,
        serializer_class=DischargeReadSerializer,
        queryset=Discharge.objects.none(),
    )
    def discharge(self, request, pk=None):
        try:
            episode = Episode.objects.select_related("discharge").get(pk=pk)
        except ObjectDoesNotExist:
            raise NotFound(f"Episode {pk=} not found.")

        try:
            data = DischargeReadSerializer(episode.discharge).data
        except AttributeError:
            data = {}

        return Response(data)

    @swagger_auto_schema(
        method="get",
        responses={
            200: openapi.Response(
                "Returns `FollowUp` objects.",
                FollowUpReadSerializer,
            ),
        },
    )
    @action(
        detail=True,
        serializer_class=FollowUpReadSerializer,
        queryset=FollowUp.objects.none(),
        url_path="follow-ups",
    )
    def follow_ups(self, request, pk=None):
        try:
            episode = Episode.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise NotFound(f"Episode {pk=} not found.")

        follow_ups = FollowUp.objects.filter(episode_id=episode.id)

        serializer = FollowUpReadSerializer(follow_ups, many=True)

        return Response(serializer.data)


@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Discharge a Patient",
        operation_description="Use this endpoint to discharge a patient. Only one Discharge can be registered "
        "for the same Episode.",
        responses={201: DischargeReadSerializer()},
    ),
)
class DischargeViewset(CreateModelMixin, GenericViewSet):
    queryset = Discharge.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return DischargeReadSerializer
        if self.action == "create":
            return DischargeWriteSerializer

        raise NotImplementedError


@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Register a Follow Up",
        operation_description="Use this endpoint to register a Follow Up. Multiple Follow Ups can be registered "
        "for the same Episode.\n "
        "\nThe accepted values for `pain_severity` are "
        f"`{FollowUp.PainSeverityChoices.labels}`.",
        responses={201: FollowUpReadSerializer()},
    ),
)
class FollowUpViewset(CreateModelMixin, GenericViewSet):
    queryset = FollowUp.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return FollowUpReadSerializer
        if self.action == "create":
            return FollowUpWriteSerializer

        raise NotImplementedError


class UnlinkedPatientsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UnlinkedPatientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user

        try:
            medical_personnel = user.medical_personnel
            preferred_hospital = medical_personnel.preferred_hospital.hospital
        except (MedicalPersonnel.DoesNotExist, PreferredHospital.DoesNotExist):
            return Patient.objects.none()

        # Subquery: check if any Episode exists for a given patient in the preferred hospital
        has_episode_subquery = Episode.objects.filter(
            patient_hospital_mapping__patient=OuterRef('pk'),
            patient_hospital_mapping__hospital=preferred_hospital
        )

        patients = Patient.objects.filter(
            hospital_mappings__hospital=preferred_hospital
        ).annotate(
            has_episode=Exists(has_episode_subquery)
        ).filter(
            has_episode=False
        ).distinct().prefetch_related('hospital_mappings')

        return patients

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class AnnouncementViewSet(ReadOnlyModelViewSet):
    serializer_class = AnnouncementSerializer

    def get_queryset(self):
        current_time = now()
        return Announcement.objects.filter(
            Q(display_from__lte=current_time) | Q(display_from__isnull=True),
            Q(display_until__gte=current_time) | Q(display_until__isnull=True)
        ).order_by("-created_at")
