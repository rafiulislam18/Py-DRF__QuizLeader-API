from rest_framework import serializers


class LeaderboardResponseSerializer(serializers.Serializer):
    username = serializers.CharField(
        help_text="Username of the player"
    )
    high_score = serializers.IntegerField(
        help_text="Highest score achieved"
    )
    avg_score = serializers.FloatField(
        help_text="Average score across all quiz play attempts"
    )
    total_played = serializers.IntegerField(
        help_text="Total number of quiz play attempts"
    )


class LeaderboardPaginatedResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        help_text="Total number of players"
    )
    next = serializers.CharField(
        help_text="URL for next page (null if no more pages)",
        allow_null=True
    )
    previous = serializers.CharField(
        help_text="URL for previous page (null if first page)",
        allow_null=True
    )
    results = LeaderboardResponseSerializer(
        help_text="List of players with stats",
        many=True
    )
