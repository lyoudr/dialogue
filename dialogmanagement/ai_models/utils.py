import os

from django.utils import timezone
from openai import OpenAI

from dialogmanagement.dialogue.models import Dialogue
from dialogmanagement.users.models import User
from dialogmanagement.utils.dialogue_types import StatusType
from dialogmanagement.utils.dialogue_types import UserType


def chat_with_ai(model, text: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    completion = client.chat.completions.create(
        model=model,  # The model you're using
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text},
        ],
        temperature=0.3,  # Lower temperature for more focused, precise answers
        max_tokens=100,  # Limit the response to 100 tokens (more concise)
        n=1,  # Generate a single response for clarity
    )
    return completion.choices[0].message.content


def record_ai_response(user_id, model, text: str):
    """Save AI response to Dialogue model"""
    user = User.objects.get(pk=user_id)
    Dialogue.objects.create(
        user=user,
        status=StatusType.COMPLETED,
        content=text,
        type=UserType.AI,
        model=model,
        created_timestamp=timezone.now(),
    )


def update_dialog_status(dialog_id: int):
    Dialogue.objects.filter(id=dialog_id).update(status=StatusType.COMPLETED)
