import random
from datetime import datetime

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
    national_id = factory.LazyAttribute(lambda n: faker.msisdn())
    day_of_birth = factory.LazyAttribute(lambda n: faker.date_of_birth().day)
    month_of_birth = factory.LazyAttribute(
        lambda n: faker.date_of_birth().month
    )
    year_of_birth = factory.LazyAttribute(lambda n: faker.date_of_birth().year)
    age = factory.LazyAttribute(
        lambda o: datetime.today().year - o.year_of_birth
    )
    gender = factory.LazyAttribute(
        lambda n: random.choice([x[0] for x in Patient.GENDER_CHOICES])
    )
    phone_1 = factory.LazyAttribute(lambda n: faker.phone_number())
    phone_2 = factory.LazyAttribute(lambda n: faker.phone_number())
    address = factory.LazyAttribute(lambda n: faker.address())
