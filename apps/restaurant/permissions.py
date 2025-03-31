from rest_framework import permissions
from .models import Cart

class IsAdminOrReadOnly(permissions.BasePermission):

    message = 'Only staff are allowed to modify'

    def has_permission(self, request, view):
        if request.method and request.method not in permissions.SAFE_METHODS:
            return request.user.is_staff
        return True

class IsOwnerOrReadOnly(permissions.IsAuthenticated):
    """
    A user is allowed to modify their own object e.g Restaurant...
    """
    message = "Not allowed for non-owner"
    def has_object_permission(self, request,view, obj):
        if request.method and request.method not in permissions.SAFE_METHODS:
            return bool(obj.owner == request.user)
        return True

class CartAlreadyExist(permissions.BasePermission):
    '''
    Restrict a user from creating their second cart. A user can have only one cart
    '''

    message = 'You already own a cart and can\'t own more than 1 cart'

    def has_permission(self, request, view):
        if request.method and request.method == 'POST':
            if Cart.objects.only('id').filter(customer=request.user).exists():
                return False
        return super().has_permission(request, view)
