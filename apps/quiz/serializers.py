from rest_framework import serializers
from .models import Question, QuizAttempt, Subject, Lesson
from rest_framework.exceptions import ValidationError


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class SubjectPaginatedResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        help_text="Total number of subjects"
    )
    next = serializers.CharField(
        help_text="URL for next page(null if no more pages)",
        allow_null=True
    )
    previous = serializers.CharField(
        help_text="URL for previous page (null if first page)",
        allow_null=True
    )
    results = SubjectSerializer(
        help_text="List of subjects",
        many=True
    )
