from django.contrib.auth import get_user_model, password_validation
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import CharField, SerializerMethodField
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    ValidationError,
)

from ..models import MedicalPersonnel

User = get_user_model()


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create(**validated_data)
            medical_personnel = MedicalPersonnel(user=user)
            medical_personnel.save()
            user.save()
            return user


class UserReadSerializer(ModelSerializer):
    medical_personnel = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "medical_personnel",
        ]

    def get_medical_personnel(self, user):
        try:
            mp = MedicalPersonnel.objects.get(user=user)
        except MedicalPersonnel.DoesNotExist:
            return None

        return {"level": mp.level, "level_display": mp.get_level_display()}


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


class ChangePasswordSerializer(Serializer):
    old_password = CharField(max_length=128, write_only=True, required=True)
    new_password1 = CharField(max_length=128, write_only=True, required=True)
    new_password2 = CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise ValidationError(
                _(
                    "Your old password was entered incorrectly. Please enter it again."
                )
            )
        return value

    def validate(self, data):
        if data["new_password1"] != data["new_password2"]:
            raise ValidationError(
                {"new_password2": _("The two password fields didn't match.")}
            )
        password_validation.validate_password(
            data["new_password1"], self.context["request"].user
        )
        return data

    def save(self, **kwargs):
        password = self.validated_data["new_password1"]
        user = self.context["request"].user
        user.set_password(password)
        user.save()
        return user
