import pytest

from apps.quiz.serializers import (
    LessonSerializer,
    LessonResponseSerializer,
    LessonPaginatedResponseSerializer
)


@pytest.mark.django_db
class TestLessonSerializers:
    def test_lesson_serializer(self, lesson):
        serializer = LessonSerializer(lesson)
        data = serializer.data
        assert data['title'] == lesson.title

    def test_lesson_response_serializer(self, lesson):
        serializer = LessonResponseSerializer(lesson)
        data = serializer.data
        assert data['id'] == lesson.id
        assert data['title'] == lesson.title
        assert data['subject']['id'] == lesson.subject.id
        assert data['subject']['name'] == lesson.subject.name

    def test_lesson_paginated_response_serializer(self, lesson):
        serializer = LessonPaginatedResponseSerializer({
            'count': 1,
            'next': None,
            'previous': None,
            'results': [lesson]
        })
        data = serializer.data
        assert data['count'] == 1
        assert data['next'] is None
        assert data['previous'] is None
        assert len(data['results']) == 1
        assert data['results'][0]['id'] == lesson.id
