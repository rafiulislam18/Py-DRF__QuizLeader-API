from django.db import models
from django.db.models import Index
from django.contrib.auth import get_user_model


User = get_user_model()


# Quiz subject
class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.id}. {self.name}"
    
    class Meta:
        indexes = [
            Index(fields=['name'], name='subject_name_idx'),
        ]


# Lesson within a subject
class Lesson(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='lessons'
    )

    def __str__(self):
        return f"{self.id}. {self.title}"
    
    class Meta:
        unique_together = ('subject', 'title')
        indexes = [
            Index(
                fields=['subject', 'title'],
                name='lesson_subject_title_idx'
            ),
        ]


# Quiz question tied to a lesson
class Question(models.Model):
    text = models.TextField()
    options = models.JSONField()  # Store 3 options as JSON: {"1": "option1", "2": "option2", "3": "option3"}
    correct_answer = models.IntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3')]
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    def __str__(self):
        return f"{self.id}. {self.text[:50]}..." if len(self.text) > 50 else f"{self.id}. {self.text}"
    
    class Meta:
        indexes = [
            Index(fields=['lesson'], name='question_lesson_idx'),
        ]
        
    def save(self, *args, **kwargs):
        # Ensure exactly 3 options
        if (
            len(self.options) != 3
            or not all(str(i) in self.options for i in range(1, 4))
        ):
            raise ValueError("Question must have exactly 3 options")
        
        super().save(*args, **kwargs)


# User's quiz attempt with scoring
class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    start_time = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}. {self.user.username} - {self.score}"
    
    class Meta:
        indexes = [
            Index(
                fields=['user', 'lesson'],
                name='attempt_user_lesson_idx'
            ),
            Index(fields=['score'], name='attempt_score_idx'),
        ]
