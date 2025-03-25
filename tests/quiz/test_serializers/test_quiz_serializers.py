import pytest

from rest_framework.exceptions import ValidationError

from apps.quiz.serializers import (
    QuizStartResponseSerializer,
    QuizSubmitSerializer,
    QuizSubmitResponseSerializer
)


@pytest.mark.django_db
class TestQuizSerializers:
    def test_quiz_start_response_serializer(self, questions, quiz_attempt):
        serializer = QuizStartResponseSerializer({
            'attempt_id': quiz_attempt.id,
            'questions': questions
        })
        data = serializer.data
        assert data['attempt_id'] == quiz_attempt.id
        assert len(data['questions']) == len(questions)
        assert data['questions'][0]['id'] == questions[0].id

    def test_quiz_submit_serializer_valid(self, questions):
        answers = {str(q.id): '1' for q in questions}
        serializer = QuizSubmitSerializer(data={'answers': answers})
        assert serializer.is_valid()
        assert serializer.validated_data['answers'] == answers

    def test_quiz_submit_serializer_empty_answers(self):
        serializer = QuizSubmitSerializer(data={'answers': {}})
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        assert 'Answers dictionary cannot be empty' in str(exc_info.value)

    def test_quiz_submit_serializer_invalid_format(self):
        serializer = QuizSubmitSerializer(data={
            'answers': {'1': 'invalid'}  # Non-digit option
        })
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        assert 'Invalid input format' in str(exc_info.value)

    def test_quiz_submit_serializer_invalid_option(self):
        serializer = QuizSubmitSerializer(data={
            'answers': {'1': '4'}  # Invalid option number
        })
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        assert 'Invalid option' in str(exc_info.value)

    def test_quiz_submit_response_serializer(self, quiz_attempt):
        serializer = QuizSubmitResponseSerializer(quiz_attempt)
        data = serializer.data
        assert data['id'] == quiz_attempt.id
        assert data['user'] == quiz_attempt.user.id
        assert data['score'] == quiz_attempt.score
        assert data['completed'] == quiz_attempt.completed
        assert data['lesson']['id'] == quiz_attempt.lesson.id
