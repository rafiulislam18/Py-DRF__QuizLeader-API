from django.urls import path
from .views import QuizStartView, QuizSubmitView, SubjectView, LessonView, QuestionView


urlpatterns = [
    path('game/start/<int:lesson_id>/', QuizStartView.as_view(), name='quiz_start'),
    path('game/submit/<int:attempt_id>/', QuizSubmitView.as_view(), name='quiz_submit'),
    path('subjects/', SubjectView.as_view(), name='subject'),
    path('lessons/<int:subject_id>/', LessonView.as_view(), name='lesson'),
    path('questions/<int:lesson_id>/', QuestionView.as_view(), name='question'),
]
