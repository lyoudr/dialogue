from celery import shared_task

from dialogmanagement.ai_models.utils import chat_with_ai
from dialogmanagement.ai_models.utils import record_ai_response
from dialogmanagement.ai_models.utils import update_dialog_status
from dialogmanagement.dialogue.models import Dialogue


@shared_task
def create_user_dialogue(user_id, content, model):
    dialogue = Dialogue.objects.create(
        user_id=user_id,
        content=content,
        model=model,
    )
    return dialogue.id


@shared_task
def chat_with_ai_task(
    dialogue_id,
    user_id,
    model,
):
    dialogue = Dialogue.objects.get(id=dialogue_id)
    text = dialogue.content
    response = chat_with_ai(model, text)
    record_ai_response(user_id, model, response)
    update_dialog_status(dialogue_id)
