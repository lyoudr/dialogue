from abc import ABC
from abc import abstractmethod

from django.utils import timezone
from openai import OpenAI

from dialogmanagement.dialog.models import Dialog
from dialogmanagement.users.models import User
from dialogmanagement.utils.dialog_types import StatusChoices
from dialogmanagement.utils.dialog_types import UserType

client = OpenAI(
    api_key="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",
)  # os.environ.get("OPENAI_API_KEY"))


class ChatAIAbstract(ABC):
    @abstractmethod
    def chat_with_ai(self, text: str) -> str:
        pass


class ChatWithAI:
    def __init__(self, user: User, model: str):
        self.user = user
        self.model = model

    def chat_with_ai(self, text: str) -> str:
        completion = client.chat.completions.create(
            model=self.model.value,  # The model you're using
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text},
            ],
            temperature=0.3,  # Lower temperature for more focused, precise answers
            max_tokens=100,  # Limit the response to 100 tokens (more concise)
            n=1,  # Generate a single response for clarity
        )
        return completion.choices[0].message.content

    def record_ai_response(self, text: str):
        """Save AI response to Dialog model"""
        Dialog.objects.create(
            user=self.user,
            status=StatusChoices.COMPLETED,
            content=text,
            type=UserType.AI,
            model=self.model,
            created_timestamp=timezone.now(),
        )

    def update_dialog_status(self, dialog: Dialog):
        dialog.status = StatusChoices.COMPLETED
        dialog.save()
