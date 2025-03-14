from celery import Task
from celery import shared_task

from dialogmanagement.dialogue.models import Dialogue
from dialogmanagement.utils.ai_service import AIModelFactory


class DialogueAITask(Task):
    """Celery task for handling AI response asynchronously."""

    def run(self, dialogue_id, user_id, model_id, model_version_id):
        """Fetch dialogue, generate AI response, and update status."""
        dialogue = Dialogue.objects.get(id=dialogue_id)
        ai_model = AIModelFactory.get_model(model_id, model_version_id)
        response = ai_model.chat_with_ai(dialogue.content)
        ai_model.save_ai_response(user_id, response)
        ai_model.update_dialogue_status(dialogue_id)


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
