import logging
import os
from abc import ABC
from abc import abstractmethod

from django.utils import timezone
from openai import OpenAI

from dialogmanagement.ai_model.models import AIModel
from dialogmanagement.ai_model.models import ModelVersion
from dialogmanagement.dialogue.models import Dialogue
from dialogmanagement.users.models import User
from dialogmanagement.utils.dialogue_types import StatusType
from dialogmanagement.utils.dialogue_types import UserType
from dialogmanagement.utils.error_handle import AIModelError
from dialogmanagement.utils.error_handle import NotFoundError


# 1. Define an Abstract Base Class for AI Models
class BaseAIModel(ABC):
    """Abstract base class for AI models."""

    def __init__(self, model_version: ModelVersion):
        self.model_version = model_version

    @abstractmethod
    def chat_with_ai(self, text: str) -> str:
        """Generate AI response."""

    def save_ai_response(self, user_id, text: str):
        """Save AI response to Dialogue model."""
        try:
            user = User.objects.get(pk=user_id)
            Dialogue.objects.create(
                user=user,
                status=StatusType.COMPLETED,
                content=text,
                type=UserType.AI,
                model=self.model_version.ai_model,
                model_version=self.model_version,
                created_timestamp=timezone.now(),
            )
        except User.DoesNotExist as err:
            raise NotFoundError(
                message=str(err),
                status_code=404,
            ) from err

    def update_dialogue_status(self, dialogue_id: int):
        """Update dialogue status to COMPLETED."""
        Dialogue.objects.filter(id=dialogue_id).update(status=StatusType.COMPLETED)


# 2. Implement Different Model Class
class ChatGPTModel(BaseAIModel):
    def __init__(self, model_version: ModelVersion):
        super().__init__(model_version)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def chat_with_ai(self, text) -> str:
        try:
            """Generate AI response using OpenAI."""
            completion = self.client.chat.completions.create(
                model=self.model_version.name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=100,
                n=1,
            )
            return completion.choices[0].message.content
        except Exception as err:
            msg = f"Unexpected error for user: {err!s}"
            logging.exception(msg)
            raise AIModelError(meassage=str(err), status_code=400) from err


# 3. Implement a Factory Class to Instantiate to the Correct AI Model
class AIModelFactory:
    """Factory class to create AI model instance."""

    MODEL_MAP = {
        "chatgpt": ChatGPTModel,
    }

    @staticmethod
    def get_model(model_id: int, model_version_id: int) -> BaseAIModel:
        """Return an instance of the requested AI model."""
        try:
            model = AIModel.objects.get(pk=model_id)
            model_version = ModelVersion.objects.get(pk=model_version_id)
        except (AIModel.DoesNotExist, ModelVersion.DoesNotExist) as err:
            raise NotFoundError(message=str(err), status_code=404) from err

        if model.name not in AIModelFactory.MODEL_MAP:
            error = f"Unsupported model: {model.name}"
            raise NotFoundError(message=error, status_code=404) from error
        return AIModelFactory.MODEL_MAP[model.name](model_version)
