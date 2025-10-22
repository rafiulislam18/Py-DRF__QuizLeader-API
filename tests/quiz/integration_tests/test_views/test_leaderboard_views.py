import pytest

from django.urls import reverse

from rest_framework import status

from apps.quiz.models import QuizAttempt


@pytest.mark.django_db
class TestSubjectLeaderboardView:
    def test_subject_leaderboard_success(self, authenticated_client, user, subject, lesson, questions):
        # Create multiple quiz attempts with different scores
        users = []
        for i in range(3):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.create_user(
                username=f'user{i}',
                password='testpass123'
            )
            users.append(user)
            
            # Create multiple attempts for each user
            for score in [10, 15, 20]:
                QuizAttempt.objects.create(
                    user=user,
                    lesson=lesson,
                    score=score,
                    completed=True
                )

        url = reverse('subject_leaderboard', kwargs={'subject_id': subject.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data
        
        # Verify data structure
        results = response.data['results']
        assert len(results) > 0
        for entry in results:
            assert 'username' in entry
            assert 'high_score' in entry
            assert 'avg_score' in entry
            assert 'total_played' in entry

    def test_subject_leaderboard_pagination(self, authenticated_client, user, subject, lesson, questions):
        # Create 15 users with different scores
        users = []
        
        # First create all users and attempts to ensure consistent data
        for i in range(15):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            new_user = User.objects.create_user(
                username=f'user{i}',
                password='testpass123'
            )
            users.append(new_user)
            
            # Create quiz attempt with decreasing scores
            QuizAttempt.objects.create(
                user=new_user,
                lesson=lesson,  # Use the same lesson (already linked to subject)
                score=30 - i,  # Decreasing scores from 30 to 16
                completed=True
            )

        # Verify data exists and is linked to the subject
        attempts = QuizAttempt.objects.filter(
            lesson__subject=subject,
            completed=True
        )
        assert attempts.count() >= 15
        
        # Test first page - should show top 10 scores only
        url = reverse('subject_leaderboard', kwargs={'subject_id': subject.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10  # Only top 10 are returned
        assert len(response.data['results']) == 10  # All 10 results on first page
        
        # Verify scores are in descending order
        scores = [entry['high_score'] for entry in response.data['results']]
        assert scores == sorted(scores, reverse=True)
        assert scores == [30, 29, 28, 27, 26, 25, 24, 23, 22, 21]  # Top 10 scores
        
        # Test second page - should be empty since we only show top 10
        response = authenticated_client.get(f"{url}?page=2")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test custom page size - should still be limited to top 10
        response = authenticated_client.get(f"{url}?page_size=15")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10  # Still only shows top 10

    def test_subject_leaderboard_no_data(self, authenticated_client, subject):
        url = reverse('subject_leaderboard', kwargs={'subject_id': subject.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "No data found for the given subject."

    def test_subject_leaderboard_invalid_subject(self, authenticated_client):
        url = reverse('subject_leaderboard', kwargs={'subject_id': 9999999999})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "No data found for the given subject."


@pytest.mark.django_db
class TestGlobalLeaderboardView:
    def test_global_leaderboard_success(self, authenticated_client, user, subject, lesson, questions):
        # Create multiple quiz attempts with different scores
        users = []
        for i in range(3):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.create_user(
                username=f'user{i}',
                password='testpass123'
            )
            users.append(user)
            
            # Create multiple attempts for each user
            for score in [10, 15, 20]:
                QuizAttempt.objects.create(
                    user=user,
                    lesson=lesson,
                    score=score,
                    completed=True
                )

        url = reverse('global_leaderboard')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data
        
        # Verify data structure
        results = response.data['results']
        assert len(results) > 0
        for entry in results:
            assert 'username' in entry
            assert 'high_score' in entry
            assert 'avg_score' in entry
            assert 'total_played' in entry

    def test_global_leaderboard_pagination(self, authenticated_client, user, subject, lesson, questions):
        # Create 30 users with different scores
        users = []
        
        # First create all users and attempts to ensure consistent data
        for i in range(30):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            new_user = User.objects.create_user(
                username=f'user{i}',
                password='testpass123'
            )
            users.append(new_user)
            
            # Create quiz attempt with decreasing scores
            QuizAttempt.objects.create(
                user=new_user,
                lesson=lesson,  # Use the same lesson
                score=50 - i,  # Decreasing scores from 50 to 21
                completed=True
            )

        # Verify data exists
        attempts = QuizAttempt.objects.filter(completed=True)
        assert attempts.count() >= 30
        
        # Test first page - should show top 25 scores only
        url = reverse('global_leaderboard')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25  # Only top 25 are returned
        assert len(response.data['results']) == 25  # All 25 results on first page
        
        # Verify scores are in descending order
        scores = [entry['high_score'] for entry in response.data['results']]
        assert scores == sorted(scores, reverse=True)
        assert scores == list(range(50, 25, -1))  # Top 25 scores
        
        # Test second page - should be empty since we only show top 25
        response = authenticated_client.get(f"{url}?page=2")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test custom page size - should still be limited to top 25
        response = authenticated_client.get(f"{url}?page_size=30")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 25  # Still only shows top 25

    def test_global_leaderboard_no_data(self, authenticated_client):
        url = reverse('global_leaderboard')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "No data found."
