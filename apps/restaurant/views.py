from django.db.models import Count
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Address ,Cuisine, FoodCategory, Restaurant, Dish, Cart , CartItem, PaymentMethod, DeliveryMethod
    )
from .serializers import ( 
     AddressSerializer,CuisineSerializer, FoodCategorySerializer, RestaurantSerializer, DishSerializer
    , CartSerializer, AddCartItemSerializer,UpdateCartItemSerializer, CartItemSerializer,PaymentMethodSerializer
    ,DeliveryMethodSerializer
                          )
from rest_framework.permissions import IsAuthenticated
from .permissions import ( IsAdminOrReadOnly, IsOwnerOrReadOnly, IsRestaurantOwnerOrReadOnly, IsCustomerOrReadOnly, 
                          AlreadyExist
                          )

# Create your views here.
class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [ IsAuthenticated ,IsOwnerOrReadOnly]

    def get_queryset(self):
        return Address.objects.select_related('owner').filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CuisineViewSet(ModelViewSet):
    '''View for cuisine. search by name, ordered by name and 
    restaurant_count: number of restaurant under the cuisine'''

    queryset = Cuisine.objects.all()
    serializer_class = CuisineSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'restaurant_count']


class FoodCategoryViewSet(ModelViewSet):
    '''View for Food category. search by name, ordered by name and 
    dish_count: number of dishes under the category'''

    queryset = FoodCategory.objects.all()
    serializer_class = FoodCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'dish_count']


class RestaurantViewSet(ModelViewSet):
    '''View for Restaurant.
    search by:
        'name', 'address', 'cuisine name', 'dishes name'
    ordered by: 
        '-is_featured', '-rating', 'name
    filter by:
        'is featured',  'rating', 'cuisine name', 'owner'

    dish_count: number of dishes by the restaurant

    permission: Only owner can modify object.
    '''
    # Currently a user can own more than one restaurant. is this okay?

    queryset = Restaurant.objects.select_related('owner', 'cuisine').prefetch_related('dishes')
    serializer_class = RestaurantSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = [
        'name', 'address', 'cuisine__name', 'dishes__name'
    ]
    filterset_fields = [
        'is_featured', 'rating', 'cuisine__name','owner'
    ]

    def get_permissions(self):
        permissions = super().get_permissions()
        # Add the custom permission 
        permissions.append(AlreadyExist(Restaurant))
        return permissions

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_context(self):
        return {'user':self.request.user}


class DishViewSet(ModelViewSet):
    '''View for  Dish. 
    search by:
        'name', 'restaurant name', 'category name'
    ordered by: 
        'is_featured', 'is_available', 'unit_price', 'name'
    filter by:
        'is_featured', 'restaurant', 'category',
        'is_vegetarian', 'is_vegan',
        'is_gluten_free',  'is_available'
    '''

    queryset = Dish.objects.select_related('restaurant', 'restaurant__cuisine'
    ).prefetch_related('category')
    serializer_class = DishSerializer
    permission_classes = [ IsRestaurantOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'restaurant__name', 'category__name']
    filterset_fields = [
        'is_featured', 'restaurant', 'category',
        'is_vegetarian', 'is_vegan',
        'is_gluten_free',  'is_available'
    ]

    def perform_create(self, serializer):
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        serializer.save(restaurant=restaurant)

    def get_serializer_context(self):
        return {'user':self.request.user}


class CartViewSet(ModelViewSet):
    '''include the Cart_id in the body to include other instruction,
    to add/increment item to/in a cart go the the cart/add-items '''

    serializer_class = CartSerializer
    permission_classes = [IsCustomerOrReadOnly]

    def get_queryset(self):
        return Cart.objects.select_related('customer').filter(customer=self.request.user)

    def get_serializer_context(self):
        '''include user and their owned address in the context.
        i am checking auth incase user isn't authenticated'''
        if self.request.user.is_authenticated:
            return {'user':self.request.user}


class AddCartItemsApiVIew(ListCreateAPIView):
    '''
    View for adding item to a cart no need to bother about creating a cart.
    add item to cart and it will create if user has no cart with the restaurant 
    you want to order dish from. If they have, we check if the item already exist
    in the restaurant cart returned if yes, we increment the quantity, else we add the new dish.
    '''

    serializer_class = AddCartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.select_related('cart').filter(cart__customer=self.request.user).order_by('updated_at')

    def get_serializer_context(self):
        return { 'user':self.request.user}


class CartItemViewset(ModelViewSet):
    queryset = CartItem.objects.all()
    http_method_names = ['get','patch','delete']
    serializer_class = CartItemSerializer

    def get_serializer_class(self):
        # if self.request.method == "POST":
        #     return AddCartItemSerializer
        if self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

 
    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['carts_pk'], 'user':self.request.user}


class PaymentMethodViewSet(ModelViewSet):
    '''CRUD payment method by only admin.'''
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['payment_type','is_active']
    ordering_fields =['is_active']

class DeliveryMethodViewSet(ModelViewSet):
    '''CRUD Delivery method by only admin.'''
    queryset = DeliveryMethod.objects.all()
    serializer_class = DeliveryMethodSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['delivery_type','is_active','base_fee']
    ordering_fields =['is_active','base_fee']
