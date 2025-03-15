from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Dialogue


class DialogueAdminChangeForm(forms.ModelForm):
    """
    Form for updating Dialogue instances in the Admin Area.
    """

    class Meta:
        model = Dialogue
        fields = ["user", "status", "content", "type", "model", "model_version"]
        error_messages = {
            "content": {
                "required": _("This field cannot be empty."),
            },
        }


class DialogueAdminCreationForm(forms.ModelForm):
    """
    Form for creating Dialogue instances in the Admin Area.
    """

    class Meta:
        model = Dialogue
        fields = ["user", "status", "content", "type", "model", "model_version"]
        error_messages = {
            "content": {
                "required": _("This field cannot be empty."),
            },
        }
