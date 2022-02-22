from django.db.models import Q
from django.utils.decorators import method_decorator
from django_filters import (  # pylint: disable=E0401
    CharFilter,
    NumberFilter,
    OrderingFilter,
)
from django_filters.rest_framework import FilterSet  # pylint: disable=E0401
from drf_yasg.openapi import IN_QUERY, TYPE_INTEGER, TYPE_STRING, Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from ..models import (
    Discharge,
    Episode,
    FollowUp,
    Hospital,
    Patient,
    PatientHospitalMapping,
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
    ReadPatientSerializer,
)


class HospitalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer


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
        if value:
            queryset = queryset.filter(
                Q(full_name__icontains=value) | Q(national_id__iexact=value)
            )
        return queryset

    class Meta:
        model = Patient
        fields = ["hospital_id", "search_term"]


@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        responses={201: ReadPatientSerializer(many=True)}
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
        operation_description="Use this endpoint to register an episode. \n ",
        responses={201: EpisodeReadSerializer()},
    ),
)
class EpisodeViewset(CreateModelMixin, GenericViewSet):
    queryset = Episode.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return EpisodeReadSerializer
        if self.action == "create":
            return EpisodeWriteSerializer

        raise NotImplementedError


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
        operation_description="Use this endpoint to register a Follow Up. Multiple Follow Ups can be registered"
        "for the same Episode.\n\n The accepted values for `pain_severity` are"
        f" `{FollowUp.PainSeverityChoices.labels}`",
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
