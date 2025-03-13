from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from dialogmanagement.dialogue.api.views import DialogueViewSet
from dialogmanagement.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("dialogue", DialogueViewSet)

app_name = "api"
urlpatterns = router.urls
