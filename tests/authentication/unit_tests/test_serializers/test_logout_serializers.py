import pytest

from apps.authentication.serializers import LogoutSerializer


@pytest.mark.django_db
class TestLogoutSerializers:
    def test_logout_serializer_valid_data(self):
        data = {
            'refresh': 'refresh_token'
        }
        serializer = LogoutSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.data == data

    def test_logout_serializer_missing_refresh(self):
        data = {}
        serializer = LogoutSerializer(data=data)
        assert not serializer.is_valid()
        assert 'refresh' in serializer.errors
