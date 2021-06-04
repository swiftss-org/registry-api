from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from tmh_registry.users.models import MedicalPersonnel

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalPersonnel
        fields = ["user"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email"]

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create(**validated_data)
            profile = MedicalPersonnel(user=user)
            profile.save()
            user.save()
            return user


class UserReadSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ["email", "profile"]


class SignInSerializer(serializers.Serializer):
    """
    Serializer responsible for input validation of sign in view
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def update(self, instance, validated_data):  # pragma: no cover
        pass

    def create(self, validated_data):  # pragma: no cover
        pass


class SignInResponseSerializer(serializers.Serializer):
    """
    Serializer responsible for output validation of sign in view
    """

    token = serializers.CharField(required=True)
    user = UserReadSerializer()

    def update(self, instance, validated_data):  # pragma: no cover
        pass

    def create(self, validated_data):  # pragma: no cover
        pass
