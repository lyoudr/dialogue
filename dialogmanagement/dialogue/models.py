from django.db import models
from django.utils import timezone

from dialogmanagement.utils.dialogue_types import ModelType
from dialogmanagement.utils.dialogue_types import StatusType
from dialogmanagement.utils.dialogue_types import UserType


# Create your models here.
class Dialogue(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="dialogs",
    )
    status = models.CharField(
        max_length=10,
        choices=StatusType.choices,
        default=StatusType.ACTIVE,
    )
    content = models.TextField()
    type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.USER,
    )
    model = models.CharField(
        max_length=20,
        choices=ModelType,
        default=ModelType.GPT_4O,
    )
    created_timestamp = models.DateTimeField(default=timezone.now)
    updated_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}-{self.user.username}"
