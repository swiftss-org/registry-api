from abc import ABC, abstractmethod
from logging import getLogger

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from tmh_registry.users.api.serializers import (
    SignInResponseSerializer,
    SignInSerializer, ChangePasswordSerializer,
)

logger = getLogger(__name__)


class BaseUserManagementView(APIView, ABC):
    """
    Base class for user management views providing utils
    """

    def get_valid_serializer(self, request):
        """
        Get serializer with g payload using proper serializer.

        :param Request request: The request received
        :raises ValidationError when payload is invalid
        :return: The serializer object
        :rtype: Serializer
        """
        data = JSONParser().parse(request)
        kwargs = {}
        serializer = self.get_serializer_class()(data=data, **kwargs)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        return serializer

    # noinspection PyMethodMayBeStatic
    def get_user_from_email(self, email):
        """
        Get the user object from the email.

        :param str email: The user email
        :return: the User
        :rtype: User
        :raises VelvontAPIException when there is no such user
        """
        user = User.objects.filter(email=email).first()
        if not user:
            raise Exception(
                f"user with email {email} " f"does not exist",
                status.HTTP_400_BAD_REQUEST,
            )
        return user

    @abstractmethod
    def get_serializer_class(self):  # pragma: no cover
        """
        Get the proper serializer. To be implemented by children.

        :return: The serializer to use
        :rtype: Serializer
        """
        pass  # pylint: disable=unnecessary-pass


class SignInView(BaseUserManagementView):
    """
    APIView for user sign in.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=SignInSerializer,
        operation_description="User login",
    )
    def post(self, request):
        """
        Handle post request.

        :param django request: The Django request
        :return: The response
        :rtype: django.response
        """
        serializer = self.get_valid_serializer(request)

        user = authenticate(
            username=serializer.data.get("username"),
            password=serializer.data.get("password"),
        )

        if not user:
            raise Exception(
                "The username and/or password provided are invalid",
                status.HTTP_400_BAD_REQUEST,
            )

        token = Token.objects.get_or_create(user=user)[0]
        return_serializer = SignInResponseSerializer(
            {"token": token, "user": user}
        )
        return Response(return_serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        """
        Get the proper serializer.

        :return: The serializer to use
        :rtype: Serializer
        """
        return SignInSerializer

class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # if using drf authtoken, create a new token
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        token, created = Token.objects.get_or_create(user=user)
        # return new token
        return Response({'token': token.key}, status=status.HTTP_200_OK)
