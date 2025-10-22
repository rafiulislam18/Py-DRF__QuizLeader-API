from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()