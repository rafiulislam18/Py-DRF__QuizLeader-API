from rest_framework import serializers


class TokenRefreshResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)
