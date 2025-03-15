from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin

from .forms import DialogueAdminChangeForm
from .forms import DialogueAdminCreationForm
from .models import Dialogue

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(Dialogue)
class DialogueAdmin(admin.ModelAdmin):
    # Specify the form to use for adding or editing
    form = DialogueAdminChangeForm
    add_form = DialogueAdminCreationForm

    # Display fields in the list view
    list_display = (
        "id",
        "user",
        "status",
        "content",
        "type",
        "model",
        "model_version",
        "created_timestamp",
        "updated_timestamp",
    )

    # Add search functionality for specific fields
    search_fields = ("user__username", "content", "status", "type")

    # Allow filtering based on certain fields
    list_filter = ("status", "type", "model", "model_version")

    # Display form with specific fields
    fieldsets = (
        (
            None,
            {"fields": ("user", "content", "status", "type", "model", "model_version")},  # noqa: 501
        ),
        ("Timestamps", {"fields": ("created_timestamp", "updated_timestamp")}),
    )

    # Enable editing of these fields directly from the list view
    list_editable = ("status", "content", "type")

    # Optional: Add inline editable features if needed for related models
    raw_id_fields = ("user", "model", "model_version")

    # Optional: Add ordering for list view
    ordering = ("created_timestamp",)

    # Optional: Limit the displayed number of items per page in the list view
    list_per_page = 20

    # Deletion is enabled by default in the admin panel
    def delete_model(self, request, obj):
        """
        Override the delete_model method to customize the deletion process if needed.
        """
        # Add any custom deletion behavior here if required.
        super().delete_model(request, obj)
