"""Defines a custom DRF permission class for the theses endpoint"""
from rest_framework.permissions import BasePermission, SAFE_METHODS

from .permissions import can_modify_thesis, can_add_thesis
from .users import wrap_user


class ThesisPermissions(BasePermission):
    """A custom permission class that determines access rights
    based on the user type (i.e. what groups the user is in) in the system
    """
    def has_object_permission(self, request, view, obj):
        """Is this request allowed on the specified object?"""
        if not request.user.is_authenticated:
            return False
        return (
            request.method in SAFE_METHODS or
            can_modify_thesis(wrap_user(request.user), obj)
        )

    def has_permission(self, request, view):
        """Is the request allowed?"""
        if not request.user.is_authenticated:
            return False
        if request.method == "POST":
            return can_add_thesis(wrap_user(request.user))
        # More specific checks we'll be required for PATCH but this
        # is handled above
        return True