import random

from django import DjangoModelFactory
from factory import LazyAttribute, SubFactory
from faker import Faker

from .models import Hospital, Patient, PatientHospitalMapping

faker = Faker()


class HospitalFactory(DjangoModelFactory):
    class Meta:
        model = Hospital

    name = LazyAttribute(lambda n: "Hospital '%s'" % faker.name())
    address = LazyAttribute(lambda n: faker.address())


class PatientFactory(DjangoModelFactory):
    class Meta:
        model = Patient

    full_name = LazyAttribute(lambda n: faker.name())
    national_id = LazyAttribute(
        lambda n: faker.numerify(text="####################")
    )
    day_of_birth = LazyAttribute(lambda n: faker.date_of_birth().day)
    month_of_birth = LazyAttribute(lambda n: faker.date_of_birth().month)
    year_of_birth = LazyAttribute(lambda n: faker.date_of_birth().year)
    gender = LazyAttribute(
        lambda n: random.choice([gender.value for gender in Patient.Gender])
    )
    phone_1 = LazyAttribute(lambda n: faker.numerify(text="#########"))
    phone_2 = LazyAttribute(lambda n: faker.numerify(text="#########"))
    address = LazyAttribute(lambda n: faker.address())


class PatientHospitalMappingFactory(DjangoModelFactory):
    class Meta:
        model = PatientHospitalMapping

    patient = SubFactory(PatientFactory)
    hospital = SubFactory(HospitalFactory)
    patient_hospital_id = LazyAttribute(lambda n: faker.ssn())
