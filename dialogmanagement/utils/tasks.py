import logging

from celery import Task
from celery import shared_task
from django.contrib.postgres.search import SearchVector

from dialogmanagement.dialogue.models import Dialogue
from dialogmanagement.utils.ai_service import AIModelFactory
from dialogmanagement.utils.error_handle import AIModelError


class DialogueAITask(Task):
    """Celery task for handling AI response asynchronously."""

    def run(self, dialogue_id, user_id, model_id, model_version_id):
        try:
            """Fetch dialogue, generate AI response, and update status."""
            dialogue = Dialogue.objects.get(id=dialogue_id)
            ai_model = AIModelFactory.get_model(model_id, model_version_id)
            response = ai_model.chat_with_ai(dialogue.content)
            ai_model.save_ai_response(user_id, response)
            ai_model.update_dialogue_status(dialogue_id)
        except Exception as err:
            msg = f"Unexpected error for user: {err!s}"
            logging.exception(msg)
            raise AIModelError(meassage=str(err), status_code=400) from err


@shared_task
def create_user_dialogue(user_id, content, model_id, model_version_id):
    dialogue = Dialogue.objects.create(
        user_id=user_id,
        content=content,
        model_id=model_id,
        model_version_id=model_version_id,
    )
    return dialogue.id


@shared_task(base=DialogueAITask)
def chat_with_ai_task(
    dialogue_id,
    user_id,
    model_id,
    model_version_id,
):
    return DialogueAITask().run(
        dialogue_id,
        user_id,
        model_id,
        model_version_id,
    )


@shared_task()
def update_search_vector(self=None):
    Dialogue.objects.update(search_vector=SearchVector("content"))
