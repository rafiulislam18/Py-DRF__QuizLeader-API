from rest_framework import serializers

from ..models import Question
from .lesson import LessonResponseSerializer


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['text', 'options', 'correct_answer']

    def validate_options(self, value):
        # Ensure exactly 3 options with keys '1', '2', '3'
        if not (
            isinstance(value, dict)
            and len(value) == 3
            and all(str(i) in value for i in range(1, 4))
        ):
            raise serializers.ValidationError(
                'Must provide exactly 3 options numbered 1-3.'
                'Example: {"1": "option1", "2": "option2", "3": "option3"}.'
                'Please check documentation for example.'
            )
        
        # Ensure no empty options
        if any(not option.strip() for option in value.values()):
            raise serializers.ValidationError(
                'Options cannot be empty.'
                'Please check documentation for example.'
            )
        
        return value


class QuestionResponseSerializer(serializers.ModelSerializer):
    lesson = LessonResponseSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'options', 'correct_answer', 'lesson']


class QuestionPaginatedResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        help_text="Total number of questions"
    )
    next = serializers.CharField(
        help_text="URL for next page (null if no more pages)",
        allow_null=True
    )
    previous = serializers.CharField(
        help_text="URL for previous page (null if first page)",
        allow_null=True
    )
    results = QuestionResponseSerializer(
        help_text="List of questions",
        many=True
    )
