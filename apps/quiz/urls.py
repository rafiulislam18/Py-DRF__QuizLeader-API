from django.urls import path

from .views import (
    QuizStartView,
    QuizSubmitView,
    SubjectLeaderboardView,
    GlobalLeaderboardView,
    SubjectListCreateView,
    SubjectDetailView,
    LessonListCreateView,
    LessonDetailView,
    QuestionListCreateView,
    QuestionDetailView
)


urlpatterns = [
    # Quiz-Game endpoints
    path('game/start/<int:lesson_id>/', QuizStartView.as_view(), name='quiz_start'),
    path('game/submit/<int:attempt_id>/', QuizSubmitView.as_view(), name='quiz_submit'),

    # Quiz-Leaderboard endpoints
    path('subjects/<int:subject_id>/leaderboard/', SubjectLeaderboardView.as_view(), name='subject_leaderboard'),
    path('leaderboard/', GlobalLeaderboardView.as_view(), name='global_leaderboard'),

    # Quiz-Subject endpoints
    path('subjects/', SubjectListCreateView.as_view(), name='subject_list_create'),
    path('subjects/<int:subject_id>/', SubjectDetailView.as_view(), name='subject_detail'),

    # Quiz-Lesson endpoints
    path('subjects/<int:subject_id>/lessons/', LessonListCreateView.as_view(), name='lesson_list_create'),
    path('lessons/<int:lesson_id>/', LessonDetailView.as_view(), name='lesson_detail'),

    # Quiz-Question endpoints
    path('lessons/<int:lesson_id>/questions/', QuestionListCreateView.as_view(), name='question_list_create'),
    path('questions/<int:question_id>/', QuestionDetailView.as_view(), name='question_detail'),
]
