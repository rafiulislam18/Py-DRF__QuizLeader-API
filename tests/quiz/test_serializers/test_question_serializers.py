import pytest

from rest_framework.exceptions import ValidationError

from apps.quiz.serializers import (
    QuestionSerializer,
    QuestionResponseSerializer,
    QuestionPaginatedResponseSerializer
)


@pytest.mark.django_db
class TestQuestionSerializers:
    def test_question_serializer(self, questions):
        question = questions[0]
        serializer = QuestionSerializer(question)
        data = serializer.data
        assert data['text'] == question.text
        assert data['options'] == question.options
        assert data['correct_answer'] == question.correct_answer

    def test_question_serializer_validation(self):
        serializer = QuestionSerializer(data={
            'text': 'Test Question',
            'options': {'1': 'A', '2': 'B'},  # Missing option 3
            'correct_answer': 1
        }, partial=True)
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        assert 'Must provide exactly 3 options' in str(exc_info.value)

    def test_question_serializer_empty_options(self):
        serializer = QuestionSerializer(data={
            'text': 'Test Question',
            'options': {'1': '', '2': 'B', '3': 'C'},  # Empty option
            'correct_answer': 1
        }, partial=True)
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        assert 'Options cannot be empty' in str(exc_info.value)

    def test_question_response_serializer(self, questions):
        question = questions[0]
        serializer = QuestionResponseSerializer(question)
        data = serializer.data
        assert data['id'] == question.id
        assert data['text'] == question.text
        assert data['options'] == question.options
        assert data['correct_answer'] == question.correct_answer
        assert data['lesson']['id'] == question.lesson.id
        assert data['lesson']['title'] == question.lesson.title

    def test_question_paginated_response_serializer(self, questions):
        serializer = QuestionPaginatedResponseSerializer({
            'count': len(questions),
            'next': None,
            'previous': None,
            'results': questions
        })
        data = serializer.data
        assert data['count'] == len(questions)
        assert data['next'] is None
        assert data['previous'] is None
        assert len(data['results']) == len(questions)
        assert data['results'][0]['id'] == questions[0].id
