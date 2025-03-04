from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    """
    Custom permission to only allow authors to access their own articles.
    """
    def has_permission(self, request, view):
        try:
            return request.user.profile.role == 'author'
        except:
            return False


class IsSecretary(permissions.BasePermission):
    """
    Custom permission to only allow secretaries to perform certain actions.
    """
    def has_permission(self, request, view):
        try:
            return request.user.profile.role == 'secretary'
        except:
            return False


class IsReviewer(permissions.BasePermission):
    """
    Custom permission to only allow reviewers to perform certain actions.
    """
    def has_permission(self, request, view):
        try:
            return request.user.profile.role == 'reviewer'
        except:
            return False


class IsEditor(permissions.BasePermission):
    """
    Custom permission to only allow editors to perform certain actions.
    """
    def has_permission(self, request, view):
        try:
            return request.user.profile.role == 'editor'
        except:
            return False


class IsDeputyEditor(permissions.BasePermission):
    """
    Custom permission to only allow deputy editors to perform certain actions.
    """
    def has_permission(self, request, view):
        try:
            return request.user.profile.role == 'deputy_editor'
        except:
            return False
