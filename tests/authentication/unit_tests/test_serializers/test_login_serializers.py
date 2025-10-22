import pytest

from rest_framework.exceptions import ValidationError

from apps.authentication.serializers import (
    LoginSerializer,
    LoginResponseSerializer
)


@pytest.mark.django_db
class TestLoginSerializers:
    def test_login_serializer_valid_data(self, user):
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        serializer = LoginSerializer(data=data, context={'request': None})
        assert serializer.is_valid()
        assert serializer.validated_data['user'] == user

    def test_login_serializer_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        serializer = LoginSerializer(data=data, context={'request': None})
        assert not serializer.is_valid()
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_login_serializer_missing_fields(self):
        data = {
            'username': 'testuser'
        }
        serializer = LoginSerializer(data=data, context={'request': None})
        assert not serializer.is_valid()
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_login_response_serializer(self, user):
        # Create the response data
        response_data = {
            'refresh': 'refresh_token',
            'access': 'access_token',
            'user': user
        }
        
        # Test the serializer
        serializer = LoginResponseSerializer(response_data)
        
        # Verify the data
        serialized_data = serializer.data
        assert serialized_data['refresh'] == response_data['refresh']
        assert serialized_data['access'] == response_data['access']
        assert serialized_data['user']['id'] == user.id
        assert serialized_data['user']['username'] == user.username
        assert serialized_data['user']['highest_score'] == user.highest_score
        assert serialized_data['user']['total_played'] == user.total_played
