import pytest

from django.urls import reverse

from rest_framework import status

from apps.authentication.models import CustomUser


@pytest.mark.django_db
class TestRegisterView:
    def test_register_success(self, api_client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'refresh' in response.data
        assert 'access' in response.data
        assert response.data['username'] == 'newuser'
        assert response.data['id'] is not None
        
        # Verify user was created in database
        user = CustomUser.objects.get(username='newuser')
        assert user.check_password('testpass123')

    def test_register_password_mismatch(self, api_client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'testpass123',
            'confirm_password': 'differentpass'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Passwords do not match' in str(response.data['detail'])

    def test_register_password_too_short(self, api_client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'short',  # less than 8 characters
            'confirm_password': 'short'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in str(response.data['detail']).lower()

    def test_register_duplicate_username(self, api_client, user):
        url = reverse('register')
        data = {
            'username': 'testuser',  # username from user fixture
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in str(response.data['detail']).lower()

    def test_register_missing_fields(self, api_client):
        url = reverse('register')
        data = {
            'username': 'newuser'
            # missing password and confirm_password
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in str(response.data['detail']).lower()
