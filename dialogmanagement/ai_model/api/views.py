from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from dialogmanagement.ai_model.models import AIModel
from dialogmanagement.ai_model.models import ModelVersion

from .serializer import AIModelSerializer
from .serializer import ModelVersionSerializer


class AIModelViewSet(ListModelMixin, GenericViewSet):
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AIModel.objects.all()


class ModelVersionViewSet(ListModelMixin, GenericViewSet):
    queryset = ModelVersion.objects.all()
    serializer_class = ModelVersionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ModelVersion.objects.all()
