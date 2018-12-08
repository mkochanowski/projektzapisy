from rest_framework.permissions import BasePermission, SAFE_METHODS

from .permissions import can_modify_thesis


class ThesisModificationPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request not in SAFE_METHODS and not can_modify_thesis(request.user, obj):
            return False
        return True
