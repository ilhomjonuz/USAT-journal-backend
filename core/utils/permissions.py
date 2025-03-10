from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author
        return obj.author == request.user


class IsSecretaryOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow secretaries to perform certain actions.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if user has secretary role
        return request.user.role == User.Role.SECRETARY


class IsReviewerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow reviewers to perform certain actions.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if user has reviewer role
        return request.user.role == User.Role.REVIEWER


class IsEditorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow editors to perform certain actions.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if user has editor role
        return request.user.role == User.Role.EDITOR


class IsDeputyOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow deputy editors to perform certain actions.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if user has deputy editor role
        return request.user.role == User.Role.DEPUTY_EDITOR
