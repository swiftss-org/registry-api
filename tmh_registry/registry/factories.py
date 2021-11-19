import random

from factory import LazyAttribute, SubFactory, post_generation
from factory.django import DjangoModelFactory
from faker import Faker

from ..users.factories import MedicalPersonnelFactory
from .models import Episode, Hospital, Patient, PatientHospitalMapping

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
    created_at = LazyAttribute(lambda n: faker.date())
    updated_at = LazyAttribute(lambda n: faker.date())
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
    patient_hospital_id = LazyAttribute(lambda _: faker.ssn())


class EpisodeFactory(DjangoModelFactory):
    class Meta:
        model = Episode

    patient_hospital_mapping = SubFactory(PatientHospitalMappingFactory)
    surgery_date = LazyAttribute(lambda _: faker.date_object())
    discharge_date = LazyAttribute(lambda _: faker.date_object())
    episode_type = LazyAttribute(
        lambda _: faker.random_element(Episode.EpisodeChoices.values)
    )
    comments = LazyAttribute(lambda _: faker.sentence(nb_words=10))
    cepod = LazyAttribute(
        lambda _: faker.random_element(Episode.CepodChoices.values)
    )
    side = LazyAttribute(
        lambda _: faker.random_element(Episode.SideChoices.values)
    )
    occurence = LazyAttribute(
        lambda _: faker.random_element(Episode.OccurenceChoices.values)
    )
    type = LazyAttribute(
        lambda _: faker.random_element(Episode.TypeChoices.values)
    )
    complexity = LazyAttribute(
        lambda _: faker.random_element(Episode.ComplexityChoices.values)
    )
    mesh_type = LazyAttribute(
        lambda _: faker.random_element(Episode.MeshTypeChoices.values)
    )
    anaesthetic_type = LazyAttribute(
        lambda _: faker.random_element(Episode.AnaestheticChoices.values)
    )
    diathermy_used = True

    @post_generation
    def medical_personnel(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            self.surgeons.add(*extracted)
        else:
            self.surgeons.add(MedicalPersonnelFactory())
