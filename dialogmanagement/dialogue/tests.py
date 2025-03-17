# Create your tests here.
from unittest.mock import MagicMock
from unittest.mock import patch

from django.test import TestCase

from dialogmanagement.ai_model.models import AIModel
from dialogmanagement.ai_model.models import ModelVersion
from dialogmanagement.users.models import User
from dialogmanagement.utils.ai_service import BaseAIModel
from dialogmanagement.utils.ai_service import ChatGPTModel
from dialogmanagement.utils.ai_service import GeminiModel
from dialogmanagement.utils.dialogue_types import StatusType
from dialogmanagement.utils.dialogue_types import UserType
from dialogmanagement.utils.error_handle import NotFoundError


class ChatGPTModelTestCase(TestCase):
    def setUp(self):
        self.model = AIModel.objects.create(name="chatgpt")
        self.model_version = ModelVersion.objects.create(
            name="gpt-4o",
            ai_model=self.model,
        )
        self.chat_model = ChatGPTModel(self.model_version)

    @patch.object(ChatGPTModel, "chat_with_ai", return_value="Mocked response")
    def test_chat_with_ai(self, mock_chat):
        # Test if chat_with_ai function is correctly mocked.
        response = self.chat_model.chat_with_ai("Hello")
        # Assertions
        self.assertEqual(response, "Mocked response")  # noqa: PT009
        mock_chat.assert_called_once_with("Hello")


class GeminiModelTestCase(TestCase):
    def setUp(self):
        self.ai_model = AIModel.objects.create(name="gemini")
        self.model_version = ModelVersion.objects.create(
            name="gemini-2.0-flash",
            ai_model=self.ai_model,
        )
        self.gemini_model = GeminiModel(self.model_version)

    @patch.object(GeminiModel, "chat_with_ai", return_value="Mocked response")
    def test_chat_with_ai(self, mock_chat):
        """Test if chat_with_ai function is correctly mocked."""

        response = self.gemini_model.chat_with_ai("Hello")

        # Assertions
        self.assertEqual(response, "Mocked response")  # noqa: PT009
        mock_chat.assert_called_once_with("Hello")


# Create a mock subclass to implement the abstract method `chat_with_ai`
class MockAIModel(BaseAIModel):
    def __init__(self, model_version):
        super().__init__(model_version)

    def chat_with_ai(self, text: str) -> str:
        return "Mock response"


class TestBaseAIModel(TestCase):
    def setUp(self):
        """Common setup for all tests."""
        self.mock_model_version = MagicMock(spec=ModelVersion)
        self.mock_model_version.ai_model = MagicMock()  # Mock AIModel
        self.mock_model_version.name = "test-model"

        self.ai_model = MockAIModel(
            self.mock_model_version,
        )  # Abstract class, only used for testing utility methods

    @patch("dialogmanagement.dialogue.models.Dialogue.objects.create")
    @patch("dialogmanagement.users.models.User.objects.get")
    @patch("django.utils.timezone.now")
    def test_save_ai_response_success(
        self,
        mock_now,
        mock_get_user,
        mock_create_dialogue,
    ):
        # Mock user retrieval
        mock_user = MagicMock(spec=User)
        mock_get_user.return_value = mock_user

        # Mock timestamp
        mock_now.return_value = "2025-03-17T12:00:00Z"

        # Call the method under test
        self.ai_model.save_ai_response(user_id=1, text="Test AI response")

        # Assertions
        mock_get_user.assert_called_once_with(pk=1)
        mock_create_dialogue.assert_called_once_with(
            user=mock_user,
            status=StatusType.COMPLETED,
            content="Test AI response",
            type=UserType.AI,
            model=self.mock_model_version.ai_model,
            model_version=self.mock_model_version,
            created_timestamp="2025-03-17T12:00:00Z",
        )

    @patch("dialogmanagement.users.models.User.objects.get")
    def test_save_ai_response_user_not_found(self, mock_get_user):
        """Test handling when user is not found."""
        mock_get_user.side_effect = User.DoesNotExist(
            "User not found",
        )  # Simulate missing user

        with self.assertRaises(NotFoundError) as context:  # noqa: PT027
            self.ai_model.save_ai_response(user_id=999, text="Test AI response")

        self.assertEqual(str(context.exception), "User not found")  # noqa: PT009

    @patch("dialogmanagement.dialogue.models.Dialogue.objects.filter")
    def test_update_dialogue_status_success(self, mock_filter):
        """Test that dialogue status is updated correctly."""
        mock_query_set = mock_filter.return_value  # Mock queryset
        mock_query_set.update = MagicMock()

        self.ai_model.update_dialogue_status(dialogue_id=5)

        mock_filter.assert_called_once_with(id=5)  # Ensure it filters correctly
        mock_query_set.update.assert_called_once_with(status=StatusType.COMPLETED)
