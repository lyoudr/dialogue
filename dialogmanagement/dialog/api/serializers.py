from rest_framework import serializers

from dialogmanagement.dialog.models import Dialog
from dialogmanagement.utils.dialog_types import StatusChoices
from dialogmanagement.utils.dialog_types import UserType


class DialogSerializer(serializers.ModelSerializer[Dialog]):
    username = serializers.SerializerMethodField()

    def get_username(self, instance):
        return instance.user.username if instance.user else None

    class Meta:
        model = Dialog
        fields = [
            "id",
            "username",
            "status",
            "type",
            "content",
            "created_timestamp",
            "updated_timestamp",
        ]


class DialogCreateSerializer(serializers.ModelSerializer[Dialog]):
    class Meta:
        model = Dialog
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
        validated_data["status"] = StatusChoices.ACTIVE
        return super().create(validated_data)
