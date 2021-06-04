from django.test import RequestFactory, TestCase
from pytest import mark

from .....users.factories import MedicalPersonnelFactory
from ....api.viewsets import HospitalViewSet
from ....factories import HospitalFactory


@mark.registry
@mark.registry.registry_viewsets
@mark.registry.registry_viewsets.hospitals
class TestHospitalsViewSet(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super(TestHospitalsViewSet, cls).setUpClass()

        cls.hospital = HospitalFactory()
        cls.medical_personnel = MedicalPersonnelFactory()

        cls.request_factory = RequestFactory()
        request = cls.request_factory.get(
            "/api/v1/users/",
            content_type="application/json",
        )
        cls.view_set = HospitalViewSet()
        cls.view_set.request = request
