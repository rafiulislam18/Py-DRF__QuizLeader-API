import pytest

from django.urls import reverse

from rest_framework import status

from apps.quiz.models import QuizAttempt


@pytest.mark.django_db
class TestQuizStartView:
    def test_quiz_start_success(self, authenticated_client, user, lesson, questions):
        url = reverse('quiz_start', kwargs={'lesson_id': lesson.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'attempt_id' in response.data
        assert 'questions' in response.data
        assert len(response.data['questions']) <= 15  # Max 15 questions
        assert len(response.data['questions']) > 0
        
        # Verify attempt was created
        attempt = QuizAttempt.objects.get(id=response.data['attempt_id'])
        assert attempt.user == user  # Fixed user access
        assert attempt.lesson == lesson
        assert attempt.score == 0
        assert not attempt.completed

    def test_quiz_start_unauthorized(self, api_client, lesson):
        url = reverse('quiz_start', kwargs={'lesson_id': lesson.id})
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_quiz_start_lesson_not_found(self, authenticated_client):
        url = reverse('quiz_start', kwargs={'lesson_id': 9999999999})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "Lesson not found."

    def test_quiz_start_no_questions(self, authenticated_client, lesson):
        # Delete all questions from the lesson
        lesson.questions.all().delete()
        
        url = reverse('quiz_start', kwargs={'lesson_id': lesson.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['attempt_id'] is not None
        assert len(response.data['questions']) == 0


@pytest.mark.django_db
class TestQuizSubmitView:
    def test_quiz_submit_success(self, authenticated_client, user, questions, quiz_attempt):
        url = reverse('quiz_submit', kwargs={'attempt_id': quiz_attempt.id})
        
        # Create answers with all correct answers
        answers = {str(q.id): str(q.correct_answer) for q in questions}
        response = authenticated_client.post(
            url, 
            {'answers': answers},
            format='json'  # Specify JSON format
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == quiz_attempt.id
        assert response.data['score'] == len(questions)  # All correct
        assert response.data['completed'] is True
        
        # Verify attempt was updated
        attempt = QuizAttempt.objects.get(id=quiz_attempt.id)
        assert attempt.score == len(questions)
        assert attempt.completed is True
        
        # Verify user stats were updated
        assert user.total_played == 1
        assert user.highest_score == len(questions)

    def test_quiz_submit_partial_score(self, authenticated_client, questions, quiz_attempt):
        url = reverse('quiz_submit', kwargs={'attempt_id': quiz_attempt.id})
        
        # Create answers with only first question correct
        answers = {}
        for i, q in enumerate(questions):
            if i == 0:
                answers[str(q.id)] = str(q.correct_answer)  # First question correct
            else:
                # For other questions, use a different answer than correct
                wrong_answer = (q.correct_answer % 3) + 1  # Will be different from correct_answer
                answers[str(q.id)] = str(wrong_answer)
        
        response = authenticated_client.post(
            url, 
            {'answers': answers},
            format='json'  # Specify JSON format
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['score'] == 1  # Only first question correct
        assert response.data['completed'] is True

    def test_quiz_submit_unauthorized(self, api_client, quiz_attempt):
        url = reverse('quiz_submit', kwargs={'attempt_id': quiz_attempt.id})
        response = api_client.post(
            url, 
            {'answers': {}},
            format='json'  # Specify JSON format
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_quiz_submit_attempt_not_found(self, authenticated_client):
        url = reverse('quiz_submit', kwargs={'attempt_id': 9999999999})
        response = authenticated_client.post(
            url, 
            {'answers': {}},
            format='json'  # Specify JSON format
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "Quiz attempt not found."

    def test_quiz_submit_already_completed(self, authenticated_client, quiz_attempt):
        # Mark attempt as completed
        quiz_attempt.completed = True
        quiz_attempt.save()
        
        url = reverse('quiz_submit', kwargs={'attempt_id': quiz_attempt.id})
        response = authenticated_client.post(
            url, 
            {'answers': {}},
            format='json'  # Specify JSON format
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['detail'] == "Quiz already completed."

    def test_quiz_submit_empty_answers(self, authenticated_client, quiz_attempt):
        url = reverse('quiz_submit', kwargs={'attempt_id': quiz_attempt.id})
        response = authenticated_client.post(
            url, 
            {'answers': {}},
            format='json'  # Specify JSON format
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Answers dictionary cannot be empty' in str(response.data['detail'])

    def test_quiz_submit_invalid_format(self, authenticated_client, quiz_attempt):
        url = reverse('quiz_submit', kwargs={'attempt_id': quiz_attempt.id})
        response = authenticated_client.post(
            url, 
            {'answers': {'1': 'invalid'}},  # Non-digit option
            format='json'  # Specify JSON format
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid input format' in str(response.data['detail'])

    def test_quiz_submit_invalid_option(self, authenticated_client, quiz_attempt):
        url = reverse('quiz_submit', kwargs={'attempt_id': quiz_attempt.id})
        response = authenticated_client.post(
            url, 
            {'answers': {'1': '4'}},  # Invalid option number
            format='json'  # Specify JSON format
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid option' in str(response.data['detail'])

    def test_quiz_submit_wrong_user(self, authenticated_client, quiz_attempt):
        # Create another user and attempt
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        other_attempt = QuizAttempt.objects.create(
            user=other_user,
            lesson=quiz_attempt.lesson,
            score=0
        )
        
        url = reverse('quiz_submit', kwargs={'attempt_id': other_attempt.id})
        response = authenticated_client.post(
            url, 
            {'answers': {}},
            format='json'  # Specify JSON format
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "Quiz attempt not found."
