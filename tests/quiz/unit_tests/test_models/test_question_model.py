import pytest

from django.core.exceptions import ValidationError

from apps.quiz.models import Question


@pytest.mark.django_db
class TestQuestion:
    def test_question_creation(self, lesson):
        options = {
            "1": "Option A",
            "2": "Option B",
            "3": "Option C"
        }
        question = Question.objects.create(
            text='What is 2 + 2?',
            options=options,
            correct_answer=1,
            lesson=lesson
        )
        assert question.text == 'What is 2 + 2?'
        assert question.options == options
        assert question.correct_answer == 1
        assert question.lesson == lesson
        assert str(question) == f"{question.id}. What is 2 + 2?"

    def test_question_options_validation(self, lesson):
        # Test with less than 3 options
        with pytest.raises(ValueError):
            Question.objects.create(
                text='Test Question',
                options={"1": "Option A", "2": "Option B"},
                correct_answer=1,
                lesson=lesson
            )

        # Test with more than 3 options
        with pytest.raises(ValueError):
            Question.objects.create(
                text='Test Question',
                options={"1": "Option A", "2": "Option B", "3": "Option C", "4": "Option D"},
                correct_answer=1,
                lesson=lesson
            )

        # Test with missing option numbers
        with pytest.raises(ValueError):
            Question.objects.create(
                text='Test Question',
                options={"1": "Option A", "2": "Option B", "4": "Option D"},
                correct_answer=1,
                lesson=lesson
            )

    def test_question_correct_answer_validation(self, lesson):
        options = {
            "1": "Option A",
            "2": "Option B",
            "3": "Option C"
        }
        question = Question(
            text='Test Question',
            options=options,
            correct_answer=4,  # Invalid choice
            lesson=lesson
        )
        with pytest.raises(ValidationError):
            question.full_clean()

    def test_question_index(self):
        indexes = Question._meta.indexes
        index_names = [index.name for index in indexes]
        assert 'question_lesson_idx' in index_names

    def test_question_limit_signal(self, lesson):
        # Test the question limit signal (max 30 questions per lesson)
        options = {
            "1": "Option A",
            "2": "Option B",
            "3": "Option C"
        }

        # Create 30 questions (should succeed)
        for i in range(30):
            Question.objects.create(
                text=f'Question {i+1}',
                options=options,
                correct_answer=1,
                lesson=lesson
            )
        
        # Try to create the 31st question (should fail)
        with pytest.raises(ValidationError) as exc_info:
            Question.objects.create(
                text='Question 31',
                options=options,
                correct_answer=1,
                lesson=lesson
            )
        assert "A lesson cannot have more than 30 questions" in str(exc_info.value)

    def test_question_limit_signal_update(self, lesson):
        # Test that the question limit signal only applies to new questions
        options = {
            "1": "Option A",
            "2": "Option B",
            "3": "Option C"
        }

        # Create a question
        question = Question.objects.create(
            text='Question 1',
            options=options,
            correct_answer=1,
            lesson=lesson
        )

        # Create 29 more questions
        for i in range(29):
            Question.objects.create(
                text=f'Question {i+2}',
                options=options,
                correct_answer=1,
                lesson=lesson
            )

        # Update existing question (should succeed)
        question.text = 'Updated Question'
        question.save()

        # Try to create a new question (should fail)
        with pytest.raises(ValidationError) as exc_info:
            Question.objects.create(
                text='Question 31',
                options=options,
                correct_answer=1,
                lesson=lesson
            )
        assert "A lesson cannot have more than 30 questions" in str(exc_info.value)
