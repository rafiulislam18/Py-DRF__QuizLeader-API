from rest_framework import serializers
from .models import CustomUser, Device
from django.core.exceptions import ValidationError


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'highest_score', 'total_played']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    device_id = serializers.CharField()
    
    def validate(self, data):
        if len(data['password']) < 8:
            raise ValidationError("Password must be at least 8 characters")
        return data


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['device_id', 'last_login']
