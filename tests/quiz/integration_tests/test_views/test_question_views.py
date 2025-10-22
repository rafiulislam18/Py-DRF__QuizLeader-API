import pytest

from django.urls import reverse
from django.core.cache import cache

from rest_framework import status

from apps.quiz.models import Question


@pytest.mark.django_db
class TestQuestionListCreateView:
    def test_list_questions_success(self, authenticated_client, lesson, questions):
        # Clear cache to ensure fresh data
        cache.clear()
        
        url = reverse('question_list_create', kwargs={'lesson_id': lesson.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data
        
        # Verify data structure and ordering
        results = response.data['results']
        assert len(results) == 15  # Default page size from QuestionListPagination
        for entry in results:
            assert set(entry.keys()) >= {'id', 'text', 'options', 'correct_answer', 'lesson'}
            assert isinstance(entry['id'], int)
            assert isinstance(entry['text'], str)
            assert isinstance(entry['options'], dict)
            assert isinstance(entry['correct_answer'], int)
            assert isinstance(entry['lesson'], dict)
            assert set(entry['lesson'].keys()) >= {'id', 'title', 'subject'}

    def test_list_questions_pagination(self, authenticated_client, lesson):
        # Clear cache to ensure fresh data
        cache.clear()
        
        # Create 30 questions
        questions = []
        for i in range(30):
            questions.append(Question.objects.create(
                text=f"Question {i}",
                options={'1': 'A', '2': 'B', '3': 'C'},
                correct_answer=1,
                lesson=lesson
            ))
        
        url = reverse('question_list_create', kwargs={'lesson_id': lesson.id})
        
        # Test first page with default size
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 15  # Default page size
        assert response.data['count'] == 30
        assert response.data['next'] is not None
        assert response.data['previous'] is None
        
        # Test second page
        response = authenticated_client.get(f"{url}?page=2")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 15
        assert response.data['next'] is None
        assert response.data['previous'] is not None
        
        # Test custom page size (up to max_page_size=30)
        response = authenticated_client.get(f"{url}?page_size=30")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 30  # Max page size
        
        # Test exceeding max page size
        response = authenticated_client.get(f"{url}?page_size=50")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 30  # Should be limited to max_page_size

    def test_list_questions_no_data(self, authenticated_client, lesson):
        # Clear cache to ensure fresh data
        cache.clear()
        
        url = reverse('question_list_create', kwargs={'lesson_id': lesson.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "No questions found for the given lesson."

    def test_list_questions_invalid_lesson(self, authenticated_client):
        url = reverse('question_list_create', kwargs={'lesson_id': 99999})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "No questions found for the given lesson."

    def test_create_question_as_admin(self, admin_client, lesson):
        url = reverse('question_list_create', kwargs={'lesson_id': lesson.id})
        data = {
            'text': 'What is 2+2?',
            'options': {
                '1': 'Three',
                '2': 'Four',
                '3': 'Five'
            },
            'correct_answer': 2
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['text'] == data['text']
        assert response.data['options'] == data['options']
        assert response.data['correct_answer'] == data['correct_answer']
        assert response.data['lesson']['id'] == lesson.id
        
        # Verify in database
        question = Question.objects.get(id=response.data['id'])
        assert question.text == data['text']
        assert question.options == data['options']
        assert question.correct_answer == data['correct_answer']
        assert question.lesson == lesson

    def test_create_question_as_staff(self, staff_client, lesson):
        url = reverse('question_list_create', kwargs={'lesson_id': lesson.id})
        data = {
            'text': 'What is 3+3?',
            'options': {
                '1': 'Five',
                '2': 'Six',
                '3': 'Seven'
            },
            'correct_answer': 2
        }
        response = staff_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['text'] == data['text']
        assert response.data['options'] == data['options']
        assert response.data['correct_answer'] == data['correct_answer']
        assert response.data['lesson']['id'] == lesson.id

    def test_create_question_as_regular_user(self, authenticated_client, lesson):
        url = reverse('question_list_create', kwargs={'lesson_id': lesson.id})
        data = {
            'text': 'What is 4+4?',
            'options': {
                '1': 'Seven',
                '2': 'Eight',
                '3': 'Nine'
            },
            'correct_answer': 2
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Question.objects.filter(text=data['text'], lesson=lesson).exists()

    def test_create_question_unauthenticated(self, api_client, lesson):
        url = reverse('question_list_create', kwargs={'lesson_id': lesson.id})
        data = {
            'text': 'What is 5+5?',
            'options': {
                '1': 'Nine',
                '2': 'Ten',
                '3': 'Eleven'
            },
            'correct_answer': 2
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not Question.objects.filter(text=data['text'], lesson=lesson).exists()

    def test_create_question_invalid_lesson(self, admin_client):
        url = reverse('question_list_create', kwargs={'lesson_id': 99999})
        data = {
            'text': 'What is 6+6?',
            'options': {
                '1': 'Eleven',
                '2': 'Twelve',
                '3': 'Thirteen'
            },
            'correct_answer': 2
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "Lesson not found."

    def test_create_question_invalid_options(self, admin_client, lesson):
        url = reverse('question_list_create', kwargs={'lesson_id': lesson.id})
        
        # Test with missing option
        data = {
            'text': 'What is 7+7?',
            'options': {
                '1': 'Thirteen',
                '2': 'Fourteen'
            },
            'correct_answer': 2
        }
        response = admin_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Test with invalid option numbers
        data = {
            'text': 'What is 7+7?',
            'options': {
                '1': 'Thirteen',
                '2': 'Fourteen',
                '4': 'Fifteen'
            },
            'correct_answer': 2
        }
        response = admin_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Test with empty option
        data = {
            'text': 'What is 7+7?',
            'options': {
                '1': 'Thirteen',
                '2': '',
                '3': 'Fifteen'
            },
            'correct_answer': 2
        }
        response = admin_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_question_invalid_correct_answer(self, admin_client, lesson):
        url = reverse('question_list_create', kwargs={'lesson_id': lesson.id})
        data = {
            'text': 'What is 8+8?',
            'options': {
                '1': 'Fifteen',
                '2': 'Sixteen',
                '3': 'Seventeen'
            },
            'correct_answer': 4  # Invalid option number
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestQuestionDetailView:
    def test_get_question_success(self, authenticated_client, questions):
        question = questions[0]
        url = reverse('question_detail', kwargs={'question_id': question.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == question.id
        assert response.data['text'] == question.text
        assert response.data['options'] == question.options
        assert response.data['correct_answer'] == question.correct_answer
        assert response.data['lesson']['id'] == question.lesson.id

    def test_get_question_not_found(self, authenticated_client):
        url = reverse('question_detail', kwargs={'question_id': 99999})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "Question not found."

    def test_update_question_put_as_admin(self, admin_client, questions):
        question = questions[0]
        url = reverse('question_detail', kwargs={'question_id': question.id})
        data = {
            'text': 'Updated question text',
            'options': {
                '1': 'New A',
                '2': 'New B',
                '3': 'New C'
            },
            'correct_answer': 3
        }
        response = admin_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['text'] == data['text']
        assert response.data['options'] == data['options']
        assert response.data['correct_answer'] == data['correct_answer']
        
        # Verify in database
        question.refresh_from_db()
        assert question.text == data['text']
        assert question.options == data['options']
        assert question.correct_answer == data['correct_answer']

    def test_update_question_patch_as_admin(self, admin_client, questions):
        question = questions[0]
        url = reverse('question_detail', kwargs={'question_id': question.id})
        data = {
            'text': 'Partially updated question'
        }
        response = admin_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['text'] == data['text']
        # Other fields should remain unchanged
        assert response.data['options'] == question.options
        assert response.data['correct_answer'] == question.correct_answer

    def test_update_question_as_staff(self, staff_client, questions):
        question = questions[0]
        url = reverse('question_detail', kwargs={'question_id': question.id})
        data = {
            'text': 'Staff updated question',
            'options': {
                '1': 'Staff A',
                '2': 'Staff B',
                '3': 'Staff C'
            },
            'correct_answer': 1
        }
        response = staff_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['text'] == data['text']
        assert response.data['options'] == data['options']
        assert response.data['correct_answer'] == data['correct_answer']

    def test_update_question_as_regular_user(self, authenticated_client, questions):
        question = questions[0]
        original_text = question.text
        url = reverse('question_detail', kwargs={'question_id': question.id})
        data = {
            'text': 'User updated question',
            'options': {
                '1': 'User A',
                '2': 'User B',
                '3': 'User C'
            },
            'correct_answer': 1
        }
        response = authenticated_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        question.refresh_from_db()
        assert question.text == original_text  # Verify no changes made

    def test_update_question_unauthenticated(self, api_client, questions):
        question = questions[0]
        original_text = question.text
        url = reverse('question_detail', kwargs={'question_id': question.id})
        data = {
            'text': 'Unauthorized update',
            'options': {
                '1': 'Unauth A',
                '2': 'Unauth B',
                '3': 'Unauth C'
            },
            'correct_answer': 1
        }
        response = api_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        question.refresh_from_db()
        assert question.text == original_text  # Verify no changes made

    def test_update_question_not_found(self, admin_client):
        url = reverse('question_detail', kwargs={'question_id': 99999})
        data = {
            'text': 'Not found question',
            'options': {
                '1': 'A',
                '2': 'B',
                '3': 'C'
            },
            'correct_answer': 1
        }
        response = admin_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "Question not found."

    def test_update_question_invalid_options(self, admin_client, questions):
        question = questions[0]
        url = reverse('question_detail', kwargs={'question_id': question.id})
        data = {
            'text': 'Invalid options',
            'options': {
                '1': 'A',
                '2': 'B'  # Missing option 3
            },
            'correct_answer': 1
        }
        response = admin_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        question.refresh_from_db()
        assert question.text != data['text']  # Verify no changes made

    def test_delete_question_as_admin(self, admin_client, questions):
        question = questions[0]
        url = reverse('question_detail', kwargs={'question_id': question.id})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Question.objects.filter(id=question.id).exists()

    def test_delete_question_as_staff(self, staff_client, questions):
        question = questions[0]
        url = reverse('question_detail', kwargs={'question_id': question.id})
        response = staff_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Question.objects.filter(id=question.id).exists()

    def test_delete_question_as_regular_user(self, authenticated_client, questions):
        question = questions[0]
        url = reverse('question_detail', kwargs={'question_id': question.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Question.objects.filter(id=question.id).exists()  # Verify question still exists

    def test_delete_question_unauthenticated(self, api_client, questions):
        question = questions[0]
        url = reverse('question_detail', kwargs={'question_id': question.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Question.objects.filter(id=question.id).exists()  # Verify question still exists

    def test_delete_question_not_found(self, admin_client):
        url = reverse('question_detail', kwargs={'question_id': 99999})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "Question not found."
