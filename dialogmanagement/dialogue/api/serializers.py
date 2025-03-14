from rest_framework import serializers

from dialogmanagement.ai_model.models import AIModel
from dialogmanagement.ai_model.models import ModelVersion
from dialogmanagement.dialogue.models import Dialogue


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
    model_id = serializers.IntegerField()
    model_version_id = serializers.IntegerField()

    class Meta:
        model = Dialogue
        fields = ["content", "model_id", "model_version_id"]

    def validate(self, attrs):
        """Validate and assign `model` and `model_version` from IDs."""
        model_id = attrs.pop("model_id")
        model_version_id = attrs.pop("model_version_id")

        # Validate AIModel existence
        try:
            ai_model = AIModel.objects.get(id=model_id)
        except AIModel.DoesNotExist as err:
            raise serializers.ValidationError(
                {"model_id": "Invalid AI model ID."},
            ) from err

        # Validate ModelVersion and ensure it belongs to AIModel
        try:
            model_version = ModelVersion.objects.get(
                id=model_version_id,
                ai_model=ai_model,
            )
        except ModelVersion.DoesNotExist as err:
            raise serializers.ValidationError(
                {
                    "model_version_id": "Invalid model version ID.",
                },
            ) from err

        # Assign validated instances
        attrs["model"] = ai_model
        attrs["model_version"] = model_version
        return attrs
