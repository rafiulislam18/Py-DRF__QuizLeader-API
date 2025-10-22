import pytest
from django.core.exceptions import ValidationError
from apps.authentication.models import CustomUser


@pytest.mark.django_db
class TestCustomUser:
    def test_given_and_default_values(self, user):
        assert user.username == 'testuser'
        assert user.highest_score == 0
        assert user.total_played == 0
        assert user.check_password('testpass123')

    def test_string_representation(self, user):
        assert str(user) == f"testuser (Score: {user.highest_score})"

    def test_field_constraints(self, user):
        # Test highest_score cannot be negative
        with pytest.raises(ValidationError):
            user.highest_score = -1
            user.full_clean()

        # Test total_played cannot be negative
        with pytest.raises(ValidationError):
            user.total_played = -1
            user.full_clean()

    def test_score_update(self, user):
        # Test updating highest score
        user.highest_score = 100
        user.save()
        assert user.highest_score == 100

        # Test updating total played
        user.total_played = 5
        user.save()
        assert user.total_played == 5

    def test_indexes(self):
        # Verify indexes are created
        indexes = CustomUser._meta.indexes
        index_names = [index.name for index in indexes]
        
        assert 'username_idx' in index_names
        assert 'high_score_idx' in index_names
