from rest_framework import serializers


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
