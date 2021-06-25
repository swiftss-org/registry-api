from django.db.models import Q
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from ..models import Hospital, Patient, PatientHospitalMapping
from .serializers import (
    CreatePatientSerializer,
    HospitalSerializer,
    PatientHospitalMappingReadSerializer,
    PatientHospitalMappingWriteSerializer,
    ReadPatientSerializer,
)


class HospitalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer


class PatientFilterSet(filters.FilterSet):
    hospital_id = filters.NumberFilter(
        method="filter_hospital",
        label="Filter based on hospital",
    )
    search_term = filters.CharFilter(
        method="filter_search_term",
        label="Filter based on search_term",
    )

    def filter_hospital(self, queryset, name, value):
        if value:
            patient_ids = PatientHospitalMapping.objects.filter(
                hospital_id=value
            ).values_list("patient_id", flat=True)
            queryset = Patient.objects.filter(id__in=patient_ids)
        return queryset

    def filter_search_term(self, queryset, name, value):
        if value:
            queryset = Patient.objects.filter(
                Q(full_name__icontains=value) | Q(national_id__icontains=value)
            )
        return queryset

    class Meta:
        model = Patient
        fields = ["hospital_id"]


@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        responses={201: ReadPatientSerializer(many=True)}
    ),
)
class PatientViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    ordering_fields = ("full_name", "day_of_birth")

    filterset_class = PatientFilterSet
    queryset = Patient.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ReadPatientSerializer
        if self.action == "create":
            return CreatePatientSerializer

        raise NotImplementedError


class PatientHospitalMappingViewset(mixins.CreateModelMixin, GenericViewSet):
    queryset = PatientHospitalMapping.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return PatientHospitalMappingReadSerializer
        if self.action == "create":
            return PatientHospitalMappingWriteSerializer

        raise NotImplementedError
