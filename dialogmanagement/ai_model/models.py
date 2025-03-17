from django.db import models

from dialogmanagement.utils.dialogue_types import GeminiModelType
from dialogmanagement.utils.dialogue_types import GPTModelType
from dialogmanagement.utils.dialogue_types import ModelType


class AIModel(models.Model):
    name = models.CharField(
        max_length=10,
        choices=ModelType.choices,
        default=ModelType.CHATGPT,
        unique=True,
    )

    def __str__(self):
        return self.name


class ModelVersion(models.Model):
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.ai_model.name} - {self.name}"

    def save(self, *args, **kwargs):
        """Ensure the version name is valid based on the AI model type before saving"""
        if (
            self.ai_model.name == ModelType.CHATGPT
            and self.name not in GPTModelType.values
        ):
            err = f"Invalid model version: {self.name}"
            raise ValueError(err)

        if (
            self.ai_model.name == ModelType.GEMINI
            and self.name not in GeminiModelType.values
        ):
            err = f"Invalid model version: {self.name}"
            raise ValueError(err)

        super().save(*args, **kwargs)
