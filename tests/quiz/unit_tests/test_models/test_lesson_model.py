import pytest

from django.core.exceptions import ValidationError

from apps.quiz.models import Lesson


@pytest.mark.django_db
class TestLesson:
    def test_lesson_creation(self, subject):
        lesson = Lesson.objects.create(
            title='Algebra Basics',
            subject=subject
        )
        assert lesson.title == 'Algebra Basics'
        assert lesson.subject == subject
        assert str(lesson) == f"{lesson.id}. Algebra Basics"

    def test_lesson_unique_together(self, subject):
        Lesson.objects.create(title='Algebra', subject=subject)
        duplicate_lesson = Lesson(title='Algebra', subject=subject)
        with pytest.raises(ValidationError):
            duplicate_lesson.full_clean()

    def test_lesson_indexes(self):
        indexes = Lesson._meta.indexes
        index_names = [index.name for index in indexes]
        assert 'lesson_subject_title_idx' in index_names
