import pytest

from django.urls import reverse

from rest_framework import status

from apps.quiz.models import Subject


@pytest.mark.django_db
class TestSubjectListCreateView:
    def test_list_subjects_success(self, authenticated_client, subject):
        # Create additional subjects
        Subject.objects.create(name="Physics")
        Subject.objects.create(name="Chemistry")
        
        url = reverse('subject_list_create')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data
        
        # Verify data structure
        results = response.data['results']
        assert len(results) == 3  # Original subject + 2 new ones
        for entry in results:
            assert 'id' in entry
            assert 'name' in entry

    def test_list_subjects_pagination(self, authenticated_client):
        # Create 15 subjects
        for i in range(15):
            Subject.objects.create(name=f"Subject {i}")
        
        url = reverse('subject_list_create')
        
        # Test first page
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10  # Default page size
        
        # Test second page
        response = authenticated_client.get(f"{url}?page=2")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5  # Remaining subjects
        
        # Test custom page size
        response = authenticated_client.get(f"{url}?page_size=15")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 15  # All subjects

    def test_list_subjects_no_data(self, authenticated_client):
        url = reverse('subject_list_create')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "No subjects found."

    def test_create_subject_as_admin(self, admin_client):
        url = reverse('subject_list_create')
        data = {'name': 'New Subject'}
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Subject'
        assert Subject.objects.filter(name='New Subject').exists()

    def test_create_subject_as_staff(self, staff_client):
        url = reverse('subject_list_create')
        data = {'name': 'New Subject'}
        response = staff_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Subject'
        assert Subject.objects.filter(name='New Subject').exists()

    def test_create_subject_as_regular_user(self, authenticated_client):
        url = reverse('subject_list_create')
        data = {'name': 'New Subject'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_subject_unauthenticated(self, api_client):
        url = reverse('subject_list_create')
        data = {'name': 'New Subject'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_subject_duplicate_name(self, admin_client, subject):
        url = reverse('subject_list_create')
        data = {'name': subject.name}  # Try to create with existing name
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestSubjectDetailView:
    def test_update_subject_put_as_admin(self, admin_client, subject):
        url = reverse('subject_detail', kwargs={'subject_id': subject.id})
        data = {'name': 'Updated Subject'}
        response = admin_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Subject'
        subject.refresh_from_db()
        assert subject.name == 'Updated Subject'

    def test_update_subject_patch_as_admin(self, admin_client, subject):
        url = reverse('subject_detail', kwargs={'subject_id': subject.id})
        data = {'name': 'Patched Subject'}
        response = admin_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Patched Subject'
        subject.refresh_from_db()
        assert subject.name == 'Patched Subject'

    def test_update_subject_as_staff(self, staff_client, subject):
        url = reverse('subject_detail', kwargs={'subject_id': subject.id})
        data = {'name': 'Staff Updated Subject'}
        response = staff_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Staff Updated Subject'
        subject.refresh_from_db()
        assert subject.name == 'Staff Updated Subject'

    def test_update_subject_as_regular_user(self, authenticated_client, subject):
        url = reverse('subject_detail', kwargs={'subject_id': subject.id})
        data = {'name': 'User Updated Subject'}
        response = authenticated_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        subject.refresh_from_db()
        assert subject.name != 'User Updated Subject'  # Verify no changes made

    def test_update_subject_unauthenticated(self, api_client, subject):
        url = reverse('subject_detail', kwargs={'subject_id': subject.id})
        data = {'name': 'Unauthorized Update'}
        response = api_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        subject.refresh_from_db()
        assert subject.name != 'Unauthorized Update'  # Verify no changes made

    def test_update_subject_not_found(self, admin_client):
        url = reverse('subject_detail', kwargs={'subject_id': 99999})
        data = {'name': 'Not Found Subject'}
        response = admin_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "Subject not found."

    def test_update_subject_duplicate_name(self, admin_client, subject):
        # Create another subject first
        other_subject = Subject.objects.create(name="Other Subject")
        
        url = reverse('subject_detail', kwargs={'subject_id': other_subject.id})
        data = {'name': subject.name}  # Try to update with existing name
        response = admin_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        other_subject.refresh_from_db()
        assert other_subject.name == "Other Subject"  # Verify no changes made

    def test_delete_subject_as_admin(self, admin_client, subject):
        url = reverse('subject_detail', kwargs={'subject_id': subject.id})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Subject.objects.filter(id=subject.id).exists()

    def test_delete_subject_as_staff(self, staff_client, subject):
        url = reverse('subject_detail', kwargs={'subject_id': subject.id})
        response = staff_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Subject.objects.filter(id=subject.id).exists()

    def test_delete_subject_as_regular_user(self, authenticated_client, subject):
        url = reverse('subject_detail', kwargs={'subject_id': subject.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Subject.objects.filter(id=subject.id).exists()

    def test_delete_subject_unauthenticated(self, api_client, subject):
        url = reverse('subject_detail', kwargs={'subject_id': subject.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Subject.objects.filter(id=subject.id).exists()

    def test_delete_subject_not_found(self, admin_client):
        url = reverse('subject_detail', kwargs={'subject_id': 99999})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "Subject not found."
