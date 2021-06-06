import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory
from faker import Faker

from .models import MedicalPersonnel

faker = Faker()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.LazyAttribute(lambda n: faker.first_name())
    last_name = factory.LazyAttribute(lambda n: faker.last_name())
    username = factory.LazyAttribute(
        lambda o: f"{o.first_name.lower()}_{o.last_name.lower()}"
    )
    email = factory.LazyAttribute(
        lambda o: "%s@example.com"
        % (o.first_name.lower() + o.last_name.lower())
    )


class MedicalPersonnelFactory(DjangoModelFactory):
    class Meta:
        model = MedicalPersonnel

    user = factory.SubFactory(UserFactory)
    level = "LEAD_SURGEON"
