from django.contrib import admin
from .models import CustomUser, Device


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'highest_score', 'total_played')
    search_fields = ('username',)
    ordering = ('-highest_score',)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_id', 'last_login')
    search_fields = ('user__username', 'device_id')
    ordering = ('-last_login',)
