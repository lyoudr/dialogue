from django.db import models


class StatusType(models.TextChoices):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETE"


class UserType(models.TextChoices):
    USER = "USER"
    AI = "AI"


class ModelType(models.TextChoices):
    CHATGPT = "chatgpt"
    LLAMA = "llama"


class GPTModelType(models.TextChoices):
    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    O1 = "o1"
    O1_PRO_MODE = "o1-pro-mode"
    O3_MINI = "o3-mini"
    O3_MINI_HIGH = "o3-mini-high"
    GPT_4_5 = "gpt-4.5"


class LLAMAModelType(models.TextChoices):
    LLAMA_2_7B = "llama-2-7b"
    LLAMA_2_13B = "llama-2-13b"
    LLAMA_2_70B = "llama-2-70b"
    LLAMA_3_8B = "llama-3-8b"
    LLAMA_3_70B = "llama-3-70b"
