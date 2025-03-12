from django.db import models
from django.utils import timezone

from dialogmanagement.utils.dialog_types import ModelChoices
from dialogmanagement.utils.dialog_types import StatusChoices
from dialogmanagement.utils.dialog_types import UserType


# Create your models here.
class Dialog(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="dialogs",
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )
    content = models.TextField()
    type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.USER,
    )
    model = models.CharField(
        max_length=20,
        choices=ModelChoices,
        default=ModelChoices.GPT_4O,
    )
    created_timestamp = models.DateTimeField(default=timezone.now)
    updated_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}-{self.user.username}"
