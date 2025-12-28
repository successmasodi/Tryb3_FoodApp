from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from apps.restaurant.documentation.restaurant.schemas import (
    cuisine_docs, food_category_docs, restaurant_docs, dish_docs,
    address_docs
)
from .models import (
<<<<<<< HEAD
    Address, Cuisine, FoodCategory, Restaurant, Dish, Cart, CartItem, PaymentMethod, DeliveryMethod,
    Order, OrderItem
)
from .serializers import (
    AddressSerializer, CuisineSerializer, FoodCategorySerializer, RestaurantSerializer, DishSerializer,
    CartSerializer, AddCartItemSerializer, PaymentMethodSerializer, DeliveryMethodSerializer,
    OrderSerializer, OrderItemSerializer
)
from rest_framework.permissions import IsAuthenticated
from .permissions import (IsAdminOrReadOnly, IsOwnerOrReadOnly, IsRestaurantOwnerOrReadOnly, IsCustomerOrReadOnly,
                          AlreadyExist
                          )

from .payment_processing import get_processor


class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
=======
    Address, Cuisine, FoodCategory, Restaurant, Dish
)
from .serializers import (
    AddressSerializer, CuisineSerializer, FoodCategorySerializer,
    RestaurantSerializer, DishSerializer
)
from .permissions import (
    IsAdminOrReadOnly, IsOwnerOrReadOnly, AlreadyExist, IsRestaurantOwnerOrReadOnly
)

class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsOwnerOrReadOnly]
>>>>>>> f753283344a55e4e45cb1213f645c638645f541f

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
<<<<<<< HEAD
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

=======
>>>>>>> f753283344a55e4e45cb1213f645c638645f541f
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
        if  Restaurant.objects.filter(owner=self.request.user).exists():
            raise ValidationError('You own a restaurant already.')
        serializer.save(owner=self.request.user)

<<<<<<< HEAD
    def get_serializer_context(self):
        return {'user': self.request.user}


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
=======
for method_name, decorator_func in restaurant_docs.items():
    RestaurantViewSet = method_decorator(decorator_func, name=method_name)(RestaurantViewSet)


class DishViewSet(ModelViewSet):
    queryset = Dish.objects.select_related('restaurant__cuisine').prefetch_related('restaurant', 'category')
>>>>>>> f753283344a55e4e45cb1213f645c638645f541f
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
        if not restaurant:
            raise ValidationError('You should own a restaurant before creating a dish.')
        serializer.save(restaurant=restaurant)

    def get_serializer_context(self):
        return {'user': self.request.user}

<<<<<<< HEAD

class CartViewSet(ModelViewSet):
    '''include the Cart_id in the body to include other instruction,
    to add/increment item to/in a cart go the cart/add-items '''

    serializer_class = CartSerializer
    permission_classes = [IsCustomerOrReadOnly]

    def get_queryset(self):
        return Cart.objects.select_related('customer').filter(customer=self.request.user)

    def get_serializer_context(self):
        '''include user and their owned address in the context.
        I am checking auth incase user isn't authenticated'''
        if self.request.user.is_authenticated:
            return {'user': self.request.user}
        return super().get_serializer_context()

    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated])
    def checkout(self, request, pk=None):

        cart = self.get_object()
        try:
            with transaction.atomic():
                self.validate_cart(cart, self.get_serializer_context())

                processor = get_processor(cart.payment_method.payment_type)
                result = processor.charge(cart.total, 'xyz', cart=cart)
                if not result:
                    return Response('payment unsuccessfully', status=status.HTTP_402_PAYMENT_REQUIRED)

                # payment successful create order and orderitem
                order = self.create_order_with_item_from_cart(cart)

                #delete the cart
                cart.delete()
                # Cart.objects.get(id=cart.id).delete()
                return Response(f'payment of {cart.total} successful new order created {order.order_number}',
                                status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Checkout failed {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def validate_cart(self, cart: Cart, context: dict):
        """Ensure cart has all required checkout components"""
        if not cart.address:
            raise ValidationError("Delivery address not set")
        if cart.address.owner != context['user']:
            raise ValidationError('Wrong Address!')
        if not cart.items.exists():
            raise ValidationError("Cannot checkout empty cart")
        if not cart.payment_method:
            raise ValidationError("Payment method not selected")
        if not cart.delivery_method:
            raise ValidationError("Delivery method not selected")

    def create_order_with_item_from_cart(self, cart: Cart):

        order = Order()
        order.customer = cart.customer
        order.restaurant_name = cart.restaurant.name
        order.status = 'confirmed'
        order.payment_status = 'paid'
        order.payment_method = cart.payment_method.payment_type
        order.delivery_method = cart.delivery_method.delivery_type
        order.subtotal = cart.sub_total
        order.delivery_fee = cart.delivery_method.base_fee
        order.total = cart.total
        order.address = cart.address.__str__
        order.special_instructions = cart.special_instructions

        order.save()

        items = [OrderItem(
            order=order,
            dish_name=item.dish.name,
            unit_price=item.dish.unit_price,
            quantity=item.quantity,

        ) for item in cart.items.all()]

        OrderItem.objects.bulk_create(items)
        return order


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
        return {'user': self.request.user}


class PaymentMethodViewSet(ModelViewSet):
    '''CRUD payment method by only admin.'''
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['payment_type', 'is_active']
    ordering_fields = ['is_active']


class DeliveryMethodViewSet(ModelViewSet):
    '''CRUD Delivery method by only admin.'''
    queryset = DeliveryMethod.objects.all()
    serializer_class = DeliveryMethodSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['delivery_type', 'is_active', 'base_fee']
    ordering_fields = ['is_active', 'base_fee']


class OrderViewSet(ModelViewSet):
    '''CRUD Order by only admin.'''
    serializer_class = OrderSerializer
    # permission_classes = [IsCustomerOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['status', 'payment_status', 'restaurant_name']
    ordering_fields = ['is_active', 'total', 'total']

    def get_queryset(self):
        return Order.objects.select_related('customer')
=======
for method_name, decorator_func in dish_docs.items():
    DishViewSet = method_decorator(name=method_name, decorator=decorator_func)(DishViewSet)
>>>>>>> f753283344a55e4e45cb1213f645c638645f541f
