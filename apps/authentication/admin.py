from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'highest_score', 'total_played')
    search_fields = ('username',)
    ordering = ('-highest_score',)
