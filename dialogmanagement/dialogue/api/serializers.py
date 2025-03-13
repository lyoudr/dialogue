from rest_framework import serializers

from dialogmanagement.dialogue.models import Dialogue
from dialogmanagement.utils.dialogue_types import StatusType
from dialogmanagement.utils.dialogue_types import UserType


class DialogueSerializer(serializers.ModelSerializer[Dialogue]):
    username = serializers.SerializerMethodField()

    def get_username(self, instance):
        return instance.user.username if instance.user else None

    class Meta:
        model = Dialogue
        fields = [
            "id",
            "username",
            "status",
            "type",
            "content",
            "created_timestamp",
            "updated_timestamp",
        ]


class DialogueCreateSerializer(serializers.ModelSerializer[Dialogue]):
    class Meta:
        model = Dialogue
        fields = ["content", "model"]
        extra_kwargs = {
            "content": {"required": True},
            "model": {"required": True},
        }

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user:
            validated_data["user"] = request.user
        validated_data["type"] = UserType.USER
        validated_data["status"] = StatusType.ACTIVE
        return super().create(validated_data)
