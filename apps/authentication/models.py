from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Index


# Custom user model with additional profile fields
class CustomUser(AbstractUser):
    highest_score = models.PositiveIntegerField(default=0)
    total_played = models.PositiveIntegerField(default=0)
    
    class Meta:
        indexes = [
            Index(fields=['username'], name='username_idx'),
            Index(fields=['highest_score'], name='high_score_idx'),
        ]


# Store device-specific authentication data (e.g. front-end generated "device ID")
class Device(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=100, unique=True)
    last_login = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            Index(fields=['device_id'], name='device_id_idx'),
        ]
