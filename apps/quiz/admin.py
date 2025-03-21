from django.contrib import admin

from .models import (
    Subject,
    Lesson,
    Question,
    QuizAttempt
)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name'
    )
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 15

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'subject'
    )
    search_fields = ('title',)
    ordering = ('subject',)
    list_per_page = 15

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'text',
        'correct_answer',
        'lesson'
    )
    search_fields = ('lesson',)
    ordering = ('lesson',)
    list_per_page = 15

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'score',
        'completed',
        'lesson'
    )
    search_fields = ('user',)
    ordering = ('-score',)
    list_per_page = 15
