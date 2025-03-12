from django.db import models


class StatusChoices(models.TextChoices):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETE"


class UserType(models.TextChoices):
    USER = "USER"
    AI = "AI"


class ModelChoices(models.TextChoices):
    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    O1 = "o1"
    O1_PRO_MODE = "o1-pro-mode"
    O3_MINI = "o3-mini"
    O3_MINI_HIGH = "o3-mini-high"
    GPT_4_5 = "gpt-4.5"
