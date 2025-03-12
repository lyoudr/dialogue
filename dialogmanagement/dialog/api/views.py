from ai_models.utils import ChatWithAI
from rest_framework import status
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from utils.types import ModelChoices

from dialogmanagement.dialog.models import Dialog
from dialogmanagement.users.models import User

from .serializers import DialogCreateSerializer
from .serializers import DialogSerializer


# Create your views here.
class DialogViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = Dialog.objects.all()
    serializer_class = DialogSerializer
    permission_required = [
        "dialogmanagement.view_dialog",
        "dialogmanagement.add_dialog",
    ]

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Override the get_serializer_class method to use a different serializer
        for the 'create' action (DialogCreateSerializer).
        """
        if self.action == "create":
            return DialogCreateSerializer
        return self.serializer_class  # Default serializer for other actions

    def chat_with_ai(self, user: User, text: str, dialog: Dialog) -> str:
        chat = ChatWithAI(
            user=user,
            model=ModelChoices.GPT_4O,
        )
        response = chat.chat_with_ai(text)
        chat.record_ai_response(response)
        chat.update_dialog_status(dialog)
        return response

    def create(self, request, *args, **kwargs):
        """
        Override the create method to handle the creation of a Dialog.
        Ensure the payload is correct and the 'id' field is excluded.
        """

        # Serialize the data
        serializer = self.get_serializer(data=request.data)

        # Validate and create the dialog object
        if serializer.is_valid():
            dialog = serializer.save()  # Save the new dialog instance
            response = self.chat_with_ai(
                request.user,
                request.data.get("content"),
                dialog,
            )
            # Return a success response with the created dialog data
            return Response(
                response,
                status=status.HTTP_201_CREATED,
            )
        # Return an error response if validation fails
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
