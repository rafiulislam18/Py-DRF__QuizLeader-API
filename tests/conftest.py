import pytest

from django.test import RequestFactory
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from apps.quiz.models import Subject, Lesson, Question, QuizAttempt


@pytest.fixture
def api_client():
    # Fixture for REST API client
    return APIClient()

@pytest.fixture
def request_factory():
    # Fixture for creating test requests
    return RequestFactory()

@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        password='testpass123'
    )

@pytest.fixture
def admin_user(db):
    # Fixture for creating an admin user
    User = get_user_model()
    return User.objects.create_superuser(
        username='admin',
        password='adminpass123',
        email='admin@example.com'
    )

@pytest.fixture
def staff_user(db):
    # Fixture for creating a staff user
    User = get_user_model()
    user = User.objects.create_user(
        username='staff',
        password='staffpass123'
    )
    user.is_staff = True
    user.save()
    return user

@pytest.fixture
def authenticated_client(api_client, user):
    # Fixture for an authenticated API client
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    # Fixture for an admin API client
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.fixture
def staff_client(api_client, staff_user):
    # Fixture for a staff API client
    api_client.force_authenticate(user=staff_user)
    return api_client

@pytest.fixture
def subject(db):
    # Fixture for creating a test subject
    return Subject.objects.create(name='Math')

@pytest.fixture
def lesson(subject):
    # Fixture for creating a test lesson
    return Lesson.objects.create(title='Algebra', subject=subject)

@pytest.fixture
def questions(lesson):
    # Fixture for creating 15 test questions
    questions = []
    for i in range(15):
        question = Question.objects.create(
            text=f'Question {i+1}',
            options={'1': 'A', '2': 'B', '3': 'C'},
            correct_answer=1,
            lesson=lesson
        )
        questions.append(question)
    return questions

@pytest.fixture
def quiz_attempt(user, lesson):
    return QuizAttempt.objects.create(
        user=user,
        score=5,  # Example score
        lesson=lesson,        
    )
