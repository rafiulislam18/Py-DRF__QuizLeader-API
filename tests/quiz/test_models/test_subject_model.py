import pytest

from django.core.exceptions import ValidationError

from apps.quiz.models import Subject


@pytest.mark.django_db
class TestSubject:
    def test_subject_creation(self):
        subject = Subject.objects.create(name='Mathematics')
        assert subject.name == 'Mathematics'
        assert str(subject) == f"{subject.id}. Mathematics"

    def test_subject_unique_name(self):
        Subject.objects.create(name='Physics')
        duplicate_subject = Subject(name='Physics')
        with pytest.raises(ValidationError):
            duplicate_subject.full_clean()

    def test_subject_index(self):
        indexes = Subject._meta.indexes
        index_names = [index.name for index in indexes]
        assert 'subject_name_idx' in index_names
