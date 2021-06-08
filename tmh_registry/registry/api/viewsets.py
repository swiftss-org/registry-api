from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from ..models import Hospital, Patient
from .serializers import (
    CreatePatientSerializer,
    HospitalSerializer,
    ReadPatientSerializer,
)


class HospitalViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer


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

    queryset = Patient.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ReadPatientSerializer
        if self.action == "create":
            return CreatePatientSerializer

        raise NotImplementedError
