from rest_framework import serializers


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField()
