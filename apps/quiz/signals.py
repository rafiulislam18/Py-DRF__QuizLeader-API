from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError

from .models import Question


@receiver(pre_save, sender=Question)
def enforce_question_limit(sender, instance, **kwargs):
    if instance.lesson.questions.count() >= 30 and not instance.pk:
        raise ValidationError(
            "A lesson cannot have more than 30 questions."
        )
