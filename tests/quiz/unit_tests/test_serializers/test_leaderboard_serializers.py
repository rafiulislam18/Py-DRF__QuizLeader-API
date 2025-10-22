import pytest

from apps.quiz.serializers import (
    LeaderboardResponseSerializer,
    LeaderboardPaginatedResponseSerializer
)


@pytest.mark.django_db
class TestLeaderboardSerializers:
    def test_leaderboard_response_serializer(self):
        data = {
            'username': 'testuser',
            'high_score': 100,
            'avg_score': 85.5,
            'total_played': 10
        }
        serializer = LeaderboardResponseSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data == data

    def test_leaderboard_paginated_response_serializer(self):
        data = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{
                'username': 'testuser',
                'high_score': 100,
                'avg_score': 85.5,
                'total_played': 10
            }]
        }
        serializer = LeaderboardPaginatedResponseSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data == data
