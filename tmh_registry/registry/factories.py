import factory
from factory.django import DjangoModelFactory
from faker import Faker

from .models import Hospital

faker = Faker()


class HospitalFactory(DjangoModelFactory):
    class Meta:
        model = Hospital

    name = factory.LazyAttribute(lambda n: "Hospital '%s'" % faker.name())
    address = factory.LazyAttribute(lambda n: faker.address())
