from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):

    message = 'Only staff are allowed to modify'

    def has_permission(self, request, view):
        if request.method and request.method not in permissions.SAFE_METHODS:
            return bool(request.user.is_staff)
        return True
    
    def has_object_permission(self, request, view, obj):
        if request.method and request.method not in permissions.SAFE_METHODS:
            return bool(request.user.is_staff)
        return True


class IsOwnerOrAuthenticated(permissions.IsAuthenticated):
    """
    An authenticated user is allowed to create while a user is allowed to modify their own object ...
    """
    message = "Not allowed for non-owner"

    def has_object_permission(self, request,view, obj):
        return bool(obj.customer == request.user)
