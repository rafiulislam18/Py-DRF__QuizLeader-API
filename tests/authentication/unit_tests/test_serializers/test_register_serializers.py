import pytest

from rest_framework.exceptions import ValidationError

from apps.authentication.serializers import (
    RegisterSerializer,
    RegisterResponseSerializer
)


@pytest.mark.django_db
class TestRegisterSerializers:
    def test_register_serializer_valid_data(self):
        data = {
            'username': 'newuser',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        
        user = serializer.save()
        assert user.username == 'newuser'
        assert user.check_password('testpass123')

    def test_register_serializer_password_mismatch(self):
        data = {
            'username': 'newuser',
            'password': 'testpass123',
            'confirm_password': 'differentpass'
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_register_serializer_password_too_short(self):
        data = {
            'username': 'newuser',
            'password': 'short',  # less than 8 characters
            'confirm_password': 'short'
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_register_response_serializer(self):
        data = {
            'refresh': 'refresh_token',
            'access': 'access_token',
            'id': 1,
            'username': 'testuser'
        }
        serializer = RegisterResponseSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.data == data
