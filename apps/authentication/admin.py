from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'highest_score', 'total_played', 'is_staff')
    search_fields = ('username', 'highest_score')
    ordering = ('-highest_score',)
    list_per_page = 15
