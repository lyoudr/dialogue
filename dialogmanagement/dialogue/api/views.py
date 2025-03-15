from celery import chain
from django.core.cache import cache
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from dialogmanagement.dialogue.models import Dialogue
from dialogmanagement.utils.dialogue_types import StatusType
from dialogmanagement.utils.tasks import chat_with_ai_task
from dialogmanagement.utils.tasks import create_user_dialogue

from .permission import DialoguePermission
from .serializers import DialogueCreateSerializer
from .serializers import DialogueSerializer


# Create your views here.
class DialogueViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = Dialogue.objects.all()
    serializer_class = DialogueSerializer
    permission_classes = [IsAuthenticated, DialoguePermission]

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        cache_key = f"user_dialogues_{self.request.user.id}"
        cached_data = cache.get(cache_key)
        latest_id_key = f"user_latest_dialogue_{self.request.user.id}"
        latest_id = cache.get(latest_id_key)

        if latest_id:
            queryset = self.queryset.filter(
                Q(user=self.request.user)
                & Q(status=StatusType.COMPLETED)
                & Q(id__gt=latest_id),
            ).order_by("id")
            cache.set(latest_id_key, queryset, timeout=60 * 3)
            return queryset

        if cached_data:
            return cached_data  # Return cached queryset
        queryset = self.queryset.filter(
            user=self.request.user,
            status=StatusType.COMPLETED,
        ).order_by("id")
        cache.set(cache_key, queryset, timeout=60 * 3)
        return queryset

    def get_serializer_class(self):
        """
        Override the get_serializer_class method to use a different serializer
        for the 'create' action (DialogCreateSerializer).
        """
        if self.action == "create":
            return DialogueCreateSerializer
        return self.serializer_class  # Default serializer for other actions

    def create(self, request, *args, **kwargs):
        """
        Override the create method to handle the creation of a Dialog.
        Ensure the payload is correct and the 'id' field is excluded.
        """

        # Serialize the data
        serializer = self.get_serializer(data=request.data)
        # Validate and create the dialogue object

        if serializer.is_valid():
            chain(
                create_user_dialogue.s(
                    request.user.id,
                    serializer.validated_data.get("content"),
                    request.data.get("model_id"),
                    request.data.get("model_version_id"),
                ),
                chat_with_ai_task.s(
                    request.user.id,
                    request.data.get("model_id"),
                    request.data.get("model_version_id"),
                ),
            ).apply_async()
            return Response(
                {"message": "Dialogue created and AI task enqueued."},
                status=status.HTTP_201_CREATED,
            )
        # Return an error response if validation fails
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["put"], url_path="update-dialogue")
    def update_dialogue(self, request, pk=None):
        """
        Update the dialogue and store the latest dialogue ID in Redis cache.
        """
        latest_dialogue = (
            Dialogue.objects.filter(user=request.user)
            .order_by("-created_timestamp")
            .first()
        )

        if not latest_dialogue:
            return Response(
                {"error": "No dialogues found for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Store the latest dialogue ID in Redis with a 1-day expiration
        cache.set(
            f"user_latest_dialogue_{request.user.id}",
            latest_dialogue.id,
            timeout=86400,
        )

        return Response(
            {"message": "Dialogue updated successfully."},
            status=status.HTTP_200_OK,
        )
