import pytest

from apps.authentication.serializers import TokenRefreshResponseSerializer


@pytest.mark.django_db
class TestTokenRefreshSerializers:
    def test_token_refresh_response_serializer(self):
        data = {
            'refresh': 'new_refresh_token'
        }
        serializer = TokenRefreshResponseSerializer(data=data)
        assert serializer.is_valid()
        
        # Verify the data
        serialized_data = serializer.data
        assert serialized_data['refresh'] == data['refresh']
        assert 'access' in serializer.fields  # Check if field exists in serializer
        assert serializer.fields['access'].read_only  # Verify it's read-only

    def test_token_refresh_response_serializer_read_only_access(self):
        data = {
            'refresh': 'new_refresh_token',
            'access': 'new_access_token'  # This should be ignored since access is read-only
        }
        serializer = TokenRefreshResponseSerializer(data=data)
        assert serializer.is_valid()
        
        # Verify access field is read-only
        assert 'access' in serializer.fields
        assert serializer.fields['access'].read_only
