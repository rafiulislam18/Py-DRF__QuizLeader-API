import pytest

from django.urls import reverse

from rest_framework import status


@pytest.mark.django_db
class TestLoginView:
    def test_login_success(self, api_client, user):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'refresh' in response.data
        assert 'access' in response.data
        assert 'user' in response.data
        assert response.data['user']['username'] == 'testuser'
        assert response.data['user']['id'] == user.id

    def test_login_invalid_credentials(self, api_client, user):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid username or password' in str(response.data['detail'])

    def test_login_missing_fields(self, api_client):
        url = reverse('login')
        data = {
            'username': 'testuser'
            # missing password
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'required' in str(response.data['detail'])

    def test_login_nonexistent_user(self, api_client):
        url = reverse('login')
        data = {
            'username': 'nonexistentuser',
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid username or password' in str(response.data['detail'])
