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
