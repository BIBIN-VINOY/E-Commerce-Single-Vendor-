from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import Address

from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    AddressSerializer,
    LogoutSerializer,
)


User = get_user_model()


# --------------------------------------------------
# USER REGISTRATION
# --------------------------------------------------

class RegisterAPIView(generics.CreateAPIView):

    queryset = User.objects.all()

    serializer_class = UserRegistrationSerializer

    permission_classes = [AllowAny]


# --------------------------------------------------
# USER PROFILE
# --------------------------------------------------

class UserProfileAPIView(generics.RetrieveUpdateAPIView):

    serializer_class = UserProfileSerializer

    permission_classes = [IsAuthenticated]

    def get_object(self):

        return self.request.user


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

class LogoutAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = LogoutSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data['refresh']

        try:

            token = RefreshToken(refresh_token)

            # Ensure the refresh token belongs to
            # the currently authenticated user.
            if str(token['user_id']) != str(request.user.pk):
                raise ValidationError({
                    'refresh': 'Token does not belong to this user.'
                })

            token.blacklist()

        except TokenError:

            raise ValidationError({
                'refresh': 'Invalid or expired refresh token.'
            })

        return Response(
            {
                'message': 'Successfully logged out.'
            },
            status=status.HTTP_200_OK
        )


# --------------------------------------------------
# ADDRESS LIST AND CREATE
# --------------------------------------------------

class AddressListCreateAPIView(generics.ListCreateAPIView):

    serializer_class = AddressSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Address.objects.filter(
            user=self.request.user
        ).order_by('-is_default', '-id')

    def perform_create(self, serializer):

        serializer.save(user=self.request.user)


# --------------------------------------------------
# ADDRESS RETRIEVE, UPDATE AND DELETE
# --------------------------------------------------

class AddressDetailAPIView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = AddressSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Address.objects.filter(
            user=self.request.user
        )


# --------------------------------------------------
# SET DEFAULT ADDRESS
# --------------------------------------------------

class SetDefaultAddressAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        with transaction.atomic():

            # Lock the user row while changing the default.
            # This serializes concurrent default-address
            # updates for the same user on databases
            # supporting select_for_update().
            User.objects.select_for_update().get(
                pk=request.user.pk
            )

            address = get_object_or_404(
                Address.objects.filter(user=request.user),
                pk=pk
            )

            # Remove default status from existing addresses.
            Address.objects.filter(
                user=request.user
            ).update(is_default=False)

            # Set selected address as default.
            address.is_default = True

            address.save(update_fields=['is_default'])

        return Response(
            {
                'message': 'Default address updated successfully.',
                'address_id': address.id
            },
            status=status.HTTP_200_OK
        )