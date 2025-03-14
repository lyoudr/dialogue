from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from dialogmanagement.ai_model.api.views import AIModelViewSet
from dialogmanagement.ai_model.api.views import ModelVersionViewSet
from dialogmanagement.dialogue.api.views import DialogueViewSet
from dialogmanagement.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("dialogue", DialogueViewSet)
router.register("aimodel", AIModelViewSet)
router.register("modelversion", ModelVersionViewSet)

app_name = "api"
urlpatterns = router.urls
