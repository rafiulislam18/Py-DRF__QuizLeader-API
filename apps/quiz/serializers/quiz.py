from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import Question, QuizAttempt
from .question import QuestionResponseSerializer
from .lesson import LessonResponseSerializer


class QuizStartResponseSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField(
        help_text="ID of the created quiz attempt"
    )
    questions = QuestionResponseSerializer(
        many=True,
        help_text="List of randomized questions for the quiz",
        read_only=True
    )


class QuizSubmitSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.CharField(),
        help_text='Dictionary of "question_id": "selected_option"'
    )

    def validate_answers(self, value):
        if len(value) == 0:
            raise ValidationError(
                "Answers dictionary cannot be empty."
                "Please check documentation for example."
            )
        
        # Check if payload format is correct
        for question_id, selected_option in value.items():
            if not question_id.isdigit() or not selected_option.isdigit():
                raise ValidationError(
                    "Invalid input format."
                    "Please check documentation for example."
                )
            # Check if selected option is valid (1, 2, or 3)
            if int(selected_option) not in [1, 2, 3]:
                raise ValidationError(
                    f"Invalid option for question {question_id}. Must be 1, 2, or 3. "
                    "Please check documentation for example."
                )
        
        # Check if all question IDs are valid
        valid_question_ids = set(str(q.id) for q in Question.objects.all())
        if not set(value.keys()).issubset(valid_question_ids):
            raise ValidationError("Invalid question IDs provided")
        
        return value


class QuizSubmitResponseSerializer(serializers.ModelSerializer):
    lesson = LessonResponseSerializer(read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'user', 'score', 'start_time', 'completed', 'lesson']
