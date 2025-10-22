import pytest

from apps.authentication.serializers import CustomUserSerializer


@pytest.mark.django_db
class TestCustomUserSerializer:
    def test_custom_user_serializer(self, user):
        serializer = CustomUserSerializer(user)
        data = serializer.data
        
        assert data['id'] == user.id
        assert data['username'] == user.username
        assert data['highest_score'] == user.highest_score
        assert data['total_played'] == user.total_played
