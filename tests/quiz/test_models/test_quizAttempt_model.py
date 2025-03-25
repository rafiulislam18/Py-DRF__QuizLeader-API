import pytest

from django.core.exceptions import ValidationError

from apps.quiz.models import QuizAttempt


@pytest.mark.django_db
class TestQuizAttempt:
    def test_quiz_attempt_creation(self, user, lesson):
        attempt = QuizAttempt.objects.create(
            user=user,
            score=85,
            lesson=lesson,
            completed=True
        )
        assert attempt.user == user
        assert attempt.score == 85
        assert attempt.lesson == lesson
        assert attempt.completed is True
        assert str(attempt) == f"{attempt.id}. {user.username} - 85"

    def test_quiz_attempt_score_validation(self, user, lesson):
        attempt = QuizAttempt(
            user=user,
            score=-1,  # Invalid score
            lesson=lesson
        )
        with pytest.raises(ValidationError):
            attempt.full_clean()

    def test_quiz_attempt_indexes(self):
        indexes = QuizAttempt._meta.indexes
        index_names = [index.name for index in indexes]
        assert 'attempt_user_lesson_idx' in index_names
        assert 'attempt_score_idx' in index_names

    def test_quiz_attempt_auto_timestamp(self, user, lesson):
        attempt = QuizAttempt.objects.create(
            user=user,
            score=90,
            lesson=lesson
        )
        assert attempt.start_time is not None
