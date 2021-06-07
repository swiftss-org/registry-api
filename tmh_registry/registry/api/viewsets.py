from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from ..models import Hospital, Patient
from .serializers import HospitalSerializer, PatientSerializer


class HospitalViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer


class PatientViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):

    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
