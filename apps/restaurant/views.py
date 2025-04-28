from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from apps.restaurant.documentation.restaurant.schemas import (
    cuisine_docs, food_category_docs, restaurant_docs, dish_docs,
    address_docs
)
from .models import (
    Address, Cuisine, FoodCategory, Restaurant, Dish, Cart, CartItem, PaymentMethod
)
from .serializers import (
    AddressSerializer, CuisineSerializer, FoodCategorySerializer, 
    RestaurantSerializer, DishSerializer, CartSerializer, 
    AddCartItemSerializer, UpdateCartItemSerializer, CartItemSerializer, 
    PaymentMethodSerializer
)
from .permissions import (
    IsAdminOrReadOnly, IsOwnerOrReadOnly, AlreadyExist, IsRestaurantOwnerOrReadOnly
)

class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Address.objects.select_related('owner').filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

for method_name, decorator_func in address_docs.items():
    AddressViewSet = method_decorator(name=method_name, decorator=decorator_func)(AddressViewSet)

class CuisineViewSet(ModelViewSet):
    queryset = Cuisine.objects.all()
    serializer_class = CuisineSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'restaurant_count']

    def destroy(self, request, *args, **kwargs):
        cuisine = self.get_object()
        if cuisine.restaurants.exists():
            return Response({'status': 'error', 'message': 'cuisine is related to one or more objects restaurant. '
                           'Remove this relation before you can delete it'}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

for method_name, decorator_func in cuisine_docs.items():
    CuisineViewSet = method_decorator(decorator_func, name=method_name)(CuisineViewSet)

class FoodCategoryViewSet(ModelViewSet):
    queryset = FoodCategory.objects.all()
    serializer_class = FoodCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'menu_count']

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        if category.dishes.exists():
            return Response({'status': 'error', 'message': 'category is related to one or more objects dishes. '
                           'Remove this relation before you can delete it.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

for method_name, decorator_func in food_category_docs.items():
    FoodCategoryViewSet = method_decorator(decorator_func, name=method_name)(FoodCategoryViewSet)

class RestaurantViewSet(ModelViewSet):
    queryset = Restaurant.objects.select_related('owner', 'cuisine').prefetch_related('dishes')
    serializer_class = RestaurantSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'address', 'cuisine__name', 'dishes__name']
    filterset_fields = ['is_featured', 'rating', 'cuisine__name', 'owner']

    def get_permissions(self):
        permissions = super().get_permissions()
        permissions.append(AlreadyExist(Restaurant))
        return permissions

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_context(self):
        return {'user': self.request.user}

for method_name, decorator_func in restaurant_docs.items():
    RestaurantViewSet = method_decorator(decorator_func, name=method_name)(RestaurantViewSet)

class DishViewSet(ModelViewSet):
    queryset = Dish.objects.select_related('restaurant__cuisine').prefetch_related('restaurant', 'category')
    serializer_class = DishSerializer
    permission_classes = [IsRestaurantOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'restaurant__name', 'category__name']
    filterset_fields = [
        'is_featured', 'restaurant', 'category',
        'is_vegetarian', 'is_vegan',
        'is_gluten_free', 'is_available'
    ]

    def perform_create(self, serializer):
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        serializer.save(restaurant=restaurant)

    def get_serializer_context(self):
        return {'user': self.request.user}

for method_name, decorator_func in dish_docs.items():
    DishViewSet = method_decorator(name=method_name, decorator=decorator_func)(DishViewSet)

class CartViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'delete']
    serializer_class = CartSerializer

    def get_permissions(self):
        permissions = super().get_permissions()
        permissions.append(AlreadyExist(Cart))
        return permissions

    def get_queryset(self):
        return Cart.objects.select_related('customer').filter(customer=self.request.user)

    def get_serializer_context(self):
        return {'user': self.request.user}

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class CartItemViewset(ModelViewSet):
    serializer_class = AddCartItemSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        if self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.select_related('cart').filter(cart__customer=self.request.user)
    
    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['carts_pk']}

class PaymentMethodViewSet(ModelViewSet):
    queryset = PaymentMethod.objects.filter()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['type', 'is_active']
    ordering_fields = ['is_active', 'processing_fee']