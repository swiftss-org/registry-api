from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer, Serializer

from tmh_registry.users.models import MedicalPersonnel

User = get_user_model()


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["email"]

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create(**validated_data)
            medical_personnel = MedicalPersonnel(user=user)
            medical_personnel.save()
            user.save()
            return user


class UserReadSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["email"]


class MedicalPersonnelSerializer(ModelSerializer):
    user = UserSerializer()
    level = CharField(source="get_level_display")

    class Meta:
        model = MedicalPersonnel
        fields = ["id", "user", "level"]


class SignInSerializer(Serializer):
    """
    Serializer responsible for input validation of sign in view
    """

    username = CharField(required=True)
    password = CharField(required=True)

    def update(self, instance, validated_data):  # pragma: no cover
        pass

    def create(self, validated_data):  # pragma: no cover
        pass


class SignInResponseSerializer(Serializer):
    """
    Serializer responsible for output validation of sign in view
    """

    token = CharField(required=True)
    user = UserReadSerializer()

    def update(self, instance, validated_data):  # pragma: no cover
        pass

    def create(self, validated_data):  # pragma: no cover
        pass
