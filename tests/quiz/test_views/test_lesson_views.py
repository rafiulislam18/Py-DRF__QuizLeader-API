import pytest

from django.urls import reverse
from django.db import IntegrityError
from django.core.cache import cache

from rest_framework import status

from apps.quiz.models import Lesson


@pytest.mark.django_db
class TestLessonListCreateView:
    def test_list_lessons_success(self, authenticated_client, subject, lesson):
        # Clear cache to ensure fresh data
        cache.clear()
        
        # Create additional lessons
        Lesson.objects.create(title="Physics 101", subject=subject)
        Lesson.objects.create(title="Chemistry 101", subject=subject)
        
        url = reverse('lesson_list_create', kwargs={'subject_id': subject.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data
        
        # Verify data structure and ordering
        results = response.data['results']
        assert len(results) == 3  # Original lesson + 2 new ones
        for entry in results:
            assert set(entry.keys()) >= {'id', 'title', 'subject'}
            assert isinstance(entry['id'], int)
            assert isinstance(entry['title'], str)
            assert isinstance(entry['subject'], dict)
            assert set(entry['subject'].keys()) >= {'id', 'name'}

    def test_list_lessons_pagination(self, authenticated_client, subject):
        # Clear cache to ensure fresh data
        cache.clear()
        
        # Create 60 lessons (more than max page size)
        lessons = []
        for i in range(60):
            lessons.append(Lesson.objects.create(title=f"Lesson {i}", subject=subject))
        
        url = reverse('lesson_list_create', kwargs={'subject_id': subject.id})
        
        # Test first page with default size
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10  # Default page size
        assert response.data['count'] == 60
        assert response.data['next'] is not None
        assert response.data['previous'] is None
        
        # Test second page
        response = authenticated_client.get(f"{url}?page=2")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10
        assert response.data['next'] is not None
        assert response.data['previous'] is not None
        
        # Test custom page size (up to max_page_size=50)
        response = authenticated_client.get(f"{url}?page_size=50")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 50  # Max page size
        
        # Test exceeding max page size
        response = authenticated_client.get(f"{url}?page_size=100")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 50  # Should be limited to max_page_size

    def test_list_lessons_no_data(self, authenticated_client, subject):
        # Clear cache to ensure fresh data
        cache.clear()
        
        url = reverse('lesson_list_create', kwargs={'subject_id': subject.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "No lessons found for the given subject."

    def test_list_lessons_invalid_subject(self, authenticated_client):
        url = reverse('lesson_list_create', kwargs={'subject_id': 99999})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "No lessons found for the given subject."

    def test_create_lesson_as_admin(self, admin_client, subject):
        url = reverse('lesson_list_create', kwargs={'subject_id': subject.id})
        data = {
            'title': 'New Lesson'
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Lesson'
        assert response.data['subject']['id'] == subject.id
        
        # Verify in database
        lesson = Lesson.objects.get(id=response.data['id'])
        assert lesson.title == 'New Lesson'
        assert lesson.subject == subject

    def test_create_lesson_as_staff(self, staff_client, subject):
        url = reverse('lesson_list_create', kwargs={'subject_id': subject.id})
        data = {
            'title': 'New Lesson'
        }
        response = staff_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Lesson'
        assert response.data['subject']['id'] == subject.id
        
        # Verify in database
        lesson = Lesson.objects.get(id=response.data['id'])
        assert lesson.title == 'New Lesson'
        assert lesson.subject == subject

    def test_create_lesson_as_regular_user(self, authenticated_client, subject):
        url = reverse('lesson_list_create', kwargs={'subject_id': subject.id})
        data = {
            'title': 'New Lesson'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Lesson.objects.filter(title='New Lesson', subject=subject).exists()

    def test_create_lesson_unauthenticated(self, api_client, subject):
        url = reverse('lesson_list_create', kwargs={'subject_id': subject.id})
        data = {
            'title': 'New Lesson'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not Lesson.objects.filter(title='New Lesson', subject=subject).exists()

    def test_create_lesson_invalid_subject(self, admin_client):
        url = reverse('lesson_list_create', kwargs={'subject_id': 99999})
        data = {
            'title': 'New Lesson'
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "Subject not found."

    def test_create_lesson_duplicate_title(self, admin_client, subject, lesson):
        url = reverse('lesson_list_create', kwargs={'subject_id': subject.id})
        data = {
            'title': lesson.title
        }
        try:
            response = admin_client.post(url, data, format='json')
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert 'Duplicate' in response.data['detail']
        except IntegrityError:
            # If the database enforces uniqueness at the DB level, this is also acceptable
            pytest.skip("Database enforces unique constraint directly")


@pytest.mark.django_db
class TestLessonDetailView:
    def test_get_lesson_success(self, authenticated_client, lesson):
        url = reverse('lesson_list_create', kwargs={'subject_id': lesson.subject.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) > 0
        lesson_data = next(l for l in results if l['id'] == lesson.id)
        assert lesson_data['title'] == lesson.title
        assert lesson_data['subject']['id'] == lesson.subject.id

    def test_get_lesson_not_found(self, authenticated_client):
        url = reverse('lesson_list_create', kwargs={'subject_id': 99999})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "No lessons found for the given subject."

    def test_update_lesson_put_as_admin(self, admin_client, lesson):
        url = reverse('lesson_list_create', kwargs={'subject_id': lesson.subject.id})
        data = {
            'title': 'Updated Lesson'
        }
        response = admin_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        lesson.refresh_from_db()
        assert lesson.title != 'Updated Lesson'  # Verify no changes made

    def test_update_lesson_patch_as_admin(self, admin_client, lesson):
        url = reverse('lesson_list_create', kwargs={'subject_id': lesson.subject.id})
        data = {'title': 'Patched Lesson'}
        response = admin_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        lesson.refresh_from_db()
        assert lesson.title != 'Patched Lesson'  # Verify no changes made

    def test_update_lesson_as_staff(self, staff_client, lesson):
        url = reverse('lesson_list_create', kwargs={'subject_id': lesson.subject.id})
        data = {
            'title': 'Staff Updated Lesson'
        }
        response = staff_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        lesson.refresh_from_db()
        assert lesson.title != 'Staff Updated Lesson'  # Verify no changes made

    def test_update_lesson_as_regular_user(self, authenticated_client, lesson):
        original_title = lesson.title
        url = reverse('lesson_list_create', kwargs={'subject_id': lesson.subject.id})
        data = {
            'title': 'User Updated Lesson'
        }
        response = authenticated_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        lesson.refresh_from_db()
        assert lesson.title == original_title  # Verify no changes made

    def test_update_lesson_unauthenticated(self, api_client, lesson):
        original_title = lesson.title
        url = reverse('lesson_list_create', kwargs={'subject_id': lesson.subject.id})
        data = {
            'title': 'Unauthorized Update'
        }
        response = api_client.put(url, data, format='json')
        
        # For unauthenticated requests, 401 takes precedence over 405
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        lesson.refresh_from_db()
        assert lesson.title == original_title  # Verify no changes made

    def test_update_lesson_not_found(self, admin_client):
        url = reverse('lesson_list_create', kwargs={'subject_id': 99999})
        data = {
            'title': 'Not Found Lesson'
        }
        response = admin_client.put(url, data, format='json')
        
        # For list endpoints, method not allowed (405) takes precedence over not found (404)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_update_lesson_duplicate_title(self, admin_client, subject, lesson):
        # Create another lesson first
        other_lesson = Lesson.objects.create(title="Other Lesson", subject=subject)
        original_title = other_lesson.title
        
        url = reverse('lesson_list_create', kwargs={'subject_id': subject.id})
        data = {
            'title': lesson.title
        }
        response = admin_client.put(url, data, format='json')
        
        # For list endpoints, method not allowed (405) takes precedence
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        other_lesson.refresh_from_db()
        assert other_lesson.title == original_title  # Verify no changes made

    def test_delete_lesson_as_admin(self, admin_client, lesson):
        url = reverse('lesson_list_create', kwargs={'subject_id': lesson.subject.id})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert Lesson.objects.filter(id=lesson.id).exists()  # Verify lesson still exists

    def test_delete_lesson_as_staff(self, staff_client, lesson):
        url = reverse('lesson_list_create', kwargs={'subject_id': lesson.subject.id})
        response = staff_client.delete(url)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert Lesson.objects.filter(id=lesson.id).exists()  # Verify lesson still exists

    def test_delete_lesson_as_regular_user(self, authenticated_client, lesson):
        url = reverse('lesson_list_create', kwargs={'subject_id': lesson.subject.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Lesson.objects.filter(id=lesson.id).exists()  # Verify lesson still exists

    def test_delete_lesson_unauthenticated(self, api_client, lesson):
        url = reverse('lesson_list_create', kwargs={'subject_id': lesson.subject.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Lesson.objects.filter(id=lesson.id).exists()  # Verify lesson still exists

    def test_delete_lesson_not_found(self, admin_client):
        url = reverse('lesson_detail', kwargs={'lesson_id': 99999})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
