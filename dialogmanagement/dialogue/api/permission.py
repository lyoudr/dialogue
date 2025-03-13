from rest_framework.permissions import BasePermission


class DialoguePermission(BasePermission):
    def has_permission(self, request, view):
        allowed_permissions = [
            "dialogue.view_dialogue",
            "dialogue.add_dialogue",
        ]
        return all(request.user.has_perm(perm) for perm in allowed_permissions)
