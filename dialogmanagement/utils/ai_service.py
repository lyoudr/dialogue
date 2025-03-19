from abc import ABC
from abc import abstractmethod

import environ
from django.core.cache import cache
from django.utils import timezone
from google import genai
from google.genai import types
from openai import OpenAI

from dialogmanagement.ai_model.models import AIModel
from dialogmanagement.ai_model.models import ModelVersion
from dialogmanagement.dialogue.models import Dialogue
from dialogmanagement.users.models import User
from dialogmanagement.utils.dialogue_types import StatusType
from dialogmanagement.utils.dialogue_types import UserType
from dialogmanagement.utils.error_handle import NotFoundError

env = environ.Env()
env.read_env()


# 1. Define an Abstract Base Class for AI Models
class BaseAIModel(ABC):
    """Abstract base class for AI models."""

    def __init__(self, model_version: ModelVersion):
        self.model_version = model_version

    @abstractmethod
    def chat_with_ai(self, user_id: int, text: str) -> str:
        """Generate AI response."""

    def save_ai_response(self, user_id: int, text: str):
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
    CACHE_TIMEOUT = 60 * 60  # 1 hour (adjust as needed)

    def __init__(self, model_version: ModelVersion):
        super().__init__(model_version)
        self.client = OpenAI(api_key=env("OPENAI_API_KEY"))

    def chat_with_ai(self, user_id: int, text: str) -> str:
        """Generate AI response using OpenAI."""
        cache_key = f"chat_history_openai_{user_id}"

        # Retrieve previous conversation history from cache
        conversation_history = cache.get(cache_key, [])

        # Append user message
        conversation_history.append({"role": "user", "content": text})
        message = [{"role": "system", "content": "You are a helpful assistant."}]
        completion = self.client.chat.completions.create(
            model=self.model_version.name,
            messages=message + conversation_history,
            temperature=0.3,
            max_tokens=100,
            n=1,
        )
        ai_res = completion.choices[0].message.content.replace("\n", " ")
        conversation_history.append({"role": "assistant", "content": ai_res})
        cache.set(cache_key, conversation_history, timeout=self.CACHE_TIMEOUT)
        return ai_res


class GeminiModel(BaseAIModel):
    CACHE_TIMEOUT = 60 * 60

    def __init__(self, model_version: ModelVersion):
        super().__init__(model_version)
        self.client = genai.Client(
            vertexai=True,
            project=env("GCP_PROJECT_ID"),
            location="us-central1",
        )
        self.generate_content_config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            max_output_tokens=100,
            response_modalities=["TEXT"],
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="OFF",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="OFF",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="OFF",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="OFF",
                ),
            ],
        )

    def chat_with_ai(self, user_id: int, text: str) -> str:
        """Generate AI response using Gemnini and store conversation history in cache."""  # noqa: E501
        cache_key = f"chat_history_gemini_{user_id}"
        # Retrieve previous conversation history from cache
        raw_history = cache.get(cache_key, [])

        # Ensure retrieved history is converted intovalid Gemini Content objects
        conversation_history = []
        for item in raw_history:
            if isinstance(item, dict) and "role" in item and "parts" in item:
                conversation_history.append(
                    types.Content(
                        role=item.get("role"),
                        parts=[
                            types.Part.from_text(text=p.get("text"))
                            for p in item["parts"]
                        ],
                    ),
                )
            else:
                conversation_history.append(item)

        # Append user's message
        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=text)],
        )
        conversation_history.append(user_content)

        resp = ""
        for chunk in self.client.models.generate_content_stream(
            model=self.model_version.name,
            contents=conversation_history,
            config=self.generate_content_config,
        ):
            resp += chunk.text + " "
        ai_res = resp.strip()

        # Append AI response to history
        assistant_content = types.Content(
            role="assistant",
            parts=[types.Part.from_text(text=ai_res)],
        )
        conversation_history.append(assistant_content)

        # Convert conversation history to a format that can be stored in cache
        serialized_history = [
            {"role": c.role, "parts": [{"text": p.text} for p in c.parts]}
            for c in conversation_history
        ]
        # Store updated conversation history in cache
        cache.set(cache_key, serialized_history, timeout=self.CACHE_TIMEOUT)
        return ai_res


# 3. Implement a Factory Class to Instantiate to the Correct AI Model
class AIModelFactory:
    """Factory class to create AI model instance."""

    MODEL_MAP = {
        "chatgpt": ChatGPTModel,
        "gemini": GeminiModel,
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
