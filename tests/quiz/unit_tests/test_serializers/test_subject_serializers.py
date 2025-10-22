import pytest

from apps.quiz.serializers import (
    SubjectSerializer,
    SubjectPaginatedResponseSerializer
)


@pytest.mark.django_db
class TestSubjectSerializers:
    def test_subject_serializer(self, subject):
        serializer = SubjectSerializer(subject)
        data = serializer.data
        assert data['id'] == subject.id
        assert data['name'] == subject.name

    def test_subject_paginated_response_serializer(self, subject):
        serializer = SubjectPaginatedResponseSerializer({
            'count': 1,
            'next': None,
            'previous': None,
            'results': [subject]
        })
        data = serializer.data
        assert data['count'] == 1
        assert data['next'] is None
        assert data['previous'] is None
        assert len(data['results']) == 1
        assert data['results'][0]['id'] == subject.id
