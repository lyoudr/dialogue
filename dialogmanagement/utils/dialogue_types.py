from django.db import models


class StatusType(models.TextChoices):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETE"


class UserType(models.TextChoices):
    USER = "USER"
    AI = "AI"


class ModelType(models.TextChoices):
    CHATGPT = "chatgpt"
    GEMINI = "gemini"


class GPTModelType(models.TextChoices):
    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    O1 = "o1"
    O1_PRO_MODE = "o1-pro-mode"
    O3_MINI = "o3-mini"
    O3_MINI_HIGH = "o3-mini-high"
    GPT_4_5 = "gpt-4.5"


class GeminiModelType(models.TextChoices):
    # Added Gemini models based on provided data
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_0_PRO_EXP_02_05 = "gemini-2.0-pro-exp-02-05"
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"
    GEMINI_2_0_FLASH_THINKING_EXP_01_21 = "gemini-2.0-flash-thinking-exp-01-21"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
