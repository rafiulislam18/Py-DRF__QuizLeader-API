from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .user import CustomUserSerializer


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            if not user:
                raise ValidationError("Invalid username or password")
        else:
            raise ValidationError("Both username and password are required")

        data['user'] = user
        return data


class LoginResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    user = CustomUserSerializer()
