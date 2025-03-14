from rest_framework import serializers

from dialogmanagement.ai_model.models import AIModel
from dialogmanagement.ai_model.models import ModelVersion


class AIModelSerializer(serializers.ModelSerializer[AIModel]):
    class Meta:
        model = AIModel
        fields = "__all__"


class ModelVersionSerializer(serializers.ModelSerializer[ModelVersion]):
    class Meta:
        model = ModelVersion
        fields = [
            "id",
            "name",
        ]
