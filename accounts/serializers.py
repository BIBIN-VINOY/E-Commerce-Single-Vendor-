from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from .models import Address


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=True
    )

    password_confirm = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User

        fields = [
            'id',
            'username',
            'email',
            'phone',
            'password',
            'password_confirm',
        ]

        read_only_fields = ['id']

    def validate(self, attrs):

        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })

        candidate_user = User(
            username=attrs.get('username'),
            email=attrs.get('email'),
            phone=attrs.get('phone', '')
        )

        validate_password(password, user=candidate_user)

        return attrs

    def create(self, validated_data):

        validated_data.pop('password_confirm')

        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [
            'id',
            'username',
            'email',
            'phone',
            'profile_image',
        ]

        read_only_fields = ['id']


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address

        fields = [
            'id',
            'address_type',
            'full_name',
            'phone_number',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'postal_code',
            'country',
            'is_default',
        ]

        read_only_fields = [
            'id',
            'is_default',
        ]


class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField(
        required=True,
        write_only=True
    )