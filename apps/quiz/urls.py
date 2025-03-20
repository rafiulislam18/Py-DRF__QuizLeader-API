from django.urls import path
from .views import SubjectView, LessonView, QuestionView


urlpatterns = [
    path('subjects/', SubjectView.as_view(), name='subject'),
    path('lessons/<int:subject_id>/', LessonView.as_view(), name='lesson'),
    path('questions/<int:lesson_id>/', QuestionView.as_view(), name='question'),
]
