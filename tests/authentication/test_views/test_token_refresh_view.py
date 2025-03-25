import pytest

from django.urls import reverse

from rest_framework import status


@pytest.mark.django_db
class TestMyTokenRefreshView:
    def test_token_refresh_success(self, api_client, user):
        # First login to get tokens
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = api_client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        original_access_token = login_response.data['access']

        # Now test token refresh
        url = reverse('token_refresh')
        data = {
            'refresh': refresh_token
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'refresh' in response.data
        assert 'access' in response.data
        assert response.data['access'] != original_access_token  # New access token
        assert response.data['refresh'] != refresh_token  # New refresh token

    def test_token_refresh_invalid_token(self, api_client):
        url = reverse('token_refresh')
        data = {
            'refresh': 'invalid_token'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'token' in str(response.data['detail']).lower()

    def test_token_refresh_missing_token(self, api_client):
        url = reverse('token_refresh')
        data = {}  # Missing refresh token
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'refresh' in str(response.data['detail']).lower()

    def test_token_refresh_expired_token(self, api_client):
        url = reverse('token_refresh')
        data = {
            'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUfghzI1NiJ9.eyJ0b2tlbl9gh0eXBlIjoicmVmcmVzaCIsImV4cCI6MTYxNjI0ODQwMCwianRpIjoiMjU5ZDM0YzYtYjM0Yy00YjM1LWE5ZDAtYjM0YzQyYjM0YzQyIiwidXNlcl9pZCI6MX0.expired_token_signature'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'token' in str(response.data['detail']).lower()

    def test_token_refresh_blacklisted_token(self, api_client, user):
        # First login to get tokens
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = api_client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']

        # Logout to blacklist the token
        logout_url = reverse('logout')
        logout_data = {
            'refresh': refresh_token
        }
        api_client.post(logout_url, logout_data, format='json')

        # Try to refresh with blacklisted token
        url = reverse('token_refresh')
        data = {
            'refresh': refresh_token
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'token' in str(response.data['detail']).lower()
