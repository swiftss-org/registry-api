import random

import factory
from factory.django import DjangoModelFactory
from faker import Faker

from .models import Hospital, Patient

faker = Faker()


class HospitalFactory(DjangoModelFactory):
    class Meta:
        model = Hospital

    name = factory.LazyAttribute(lambda n: "Hospital '%s'" % faker.name())
    address = factory.LazyAttribute(lambda n: faker.address())


class PatientFactory(DjangoModelFactory):
    class Meta:
        model = Patient

    first_name = factory.LazyAttribute(lambda n: faker.first_name())
    last_name = factory.LazyAttribute(lambda n: faker.last_name())
    national_id = factory.LazyAttribute(
        lambda n: faker.numerify(text="####################")
    )
    day_of_birth = factory.LazyAttribute(lambda n: faker.date_of_birth().day)
    month_of_birth = factory.LazyAttribute(
        lambda n: faker.date_of_birth().month
    )
    year_of_birth = factory.LazyAttribute(lambda n: faker.date_of_birth().year)
    gender = factory.LazyAttribute(
        lambda n: random.choice([gender.value for gender in Patient.Gender])
    )
    phone_1 = factory.LazyAttribute(lambda n: faker.numerify(text="#########"))
    phone_2 = factory.LazyAttribute(lambda n: faker.numerify(text="#########"))
    address = factory.LazyAttribute(lambda n: faker.address())
