from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):

    message = 'Only staff are allowed to modify'

    def has_permission(self, request, view):
        if request.method and request.method not in permissions.SAFE_METHODS:
            return request.user.is_staff
        return True


class IsOwnerOrReadOnly(permissions.IsAuthenticated):
    """
    An authenticated user is allowed to create while a user is allowed to modify their own object e.g Restaurant...
    """
    message = "Not allowed for non-owner"

    def has_object_permission(self, request,view, obj):
        if request.method and request.method not in permissions.SAFE_METHODS:
            return bool(obj.owner == request.user)
        return True


class IsCustomerOrReadOnly(IsOwnerOrReadOnly):
    """
    Only customer are allowed to modify their own object.
    """
    def has_object_permission(self, request, view, obj):
        if request.method and request.method not in permissions.SAFE_METHODS:
            return bool(obj.customer == request.user)
        return True


class IsRestaurantOwnerOrReadOnly(IsOwnerOrReadOnly):
    """
    It inherits from the 'IsOwnerOrReadOnly' permission
    Only owner of restaurant that  own the dish can modify it.

    """
    message = "Your restaurant doesn't make this meal."

    def has_object_permission(self, request,view, obj):
        if request.method and request.method not in permissions.SAFE_METHODS:
            return bool(obj.restaurant.owner == request.user)
        return True


class AlreadyExist(permissions.BasePermission):
    '''
    Used to enforce OneToOne field so we don't throw an error
    Restrict a user from creating their second cart or restaurant. A user can have only one cart/restaurant.
    '''

    def __init__(self, model=None):
        self.model = model

    message = "You can't create another {self.model}"

    def has_permission(self, request, view):
        if request.method and request.method == 'POST':
            if hasattr(self.model,'owner'):
                if self.model.objects.only('id').filter(owner=request.user).exists():
                    return False

        if hasattr(self.model,'customer'):
            if Cart.objects.only('id').filter(customer=request.user).exists():
                return False

        return super().has_permission(request, view)


class AlreadyExist(permissions.BasePermission):
    '''
    Used to enforce OneToOne field so we don't throw an error.
    Restrict a user from creating their second cart or restaurant.
    A user can have only one cart/restaurant.
    '''

    def __init__(self, model=None):
        self.model = model

    def get_message(self):
        return f"You can't create another {self.model.__name__}"

    def has_permission(self, request, view):
        if request.method == 'POST':
            # Checking if the model has 'owner' attribute (for Restaurant)
            if hasattr(self.model, 'owner'):
                if self.model.objects.filter(owner=request.user).exists():
                    self.message = self.get_message()
                    return False

            # Check if the model has 'customer' attribute
            if hasattr(self.model, 'customer'):
                if self.model.objects.filter(customer=request.user).exists():
                    self.message = self.get_message()
                    return False
        return True
