from rest_framework import serializers


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class LogoutResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
