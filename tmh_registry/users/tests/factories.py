import factory
from django.contrib.auth.models import User
from faker import Factory

faker = Factory.create()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda _: faker.name())
    email = factory.LazyAttribute(lambda _: faker.email())
