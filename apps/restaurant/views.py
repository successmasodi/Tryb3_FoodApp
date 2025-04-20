from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from .models import (
    Address, Cuisine, FoodCategory, Restaurant, Dish, Cart, CartItem, PaymentMethod, DeliveryMethod,
    Order, OrderItem
)
from .serializers import (
     AddressSerializer, CuisineSerializer, FoodCategorySerializer, RestaurantSerializer, DishSerializer,
     CartSerializer, AddCartItemSerializer, PaymentMethodSerializer, DeliveryMethodSerializer,
    OrderSerializer, OrderItemSerializer
    )
from .permissions import (IsAdminOrReadOnly, IsOwnerOrReadOnly, IsRestaurantOwnerOrReadOnly, IsCustomerOrReadOnly,
                           AlreadyExist
                           )
from .utils import decrypt_token

from .payment_processing import get_processor
# Create your views here.


class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

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

    queryset = Restaurant.objects.select_related(
        'owner', 'cuisine').prefetch_related('dishes')
    serializer_class = RestaurantSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = [
        'name', 'address', 'cuisine__name', 'dishes__name'
    ]
    filterset_fields = [
        'is_featured', 'rating', 'cuisine__name', 'owner'
    ]

    def get_permissions(self):
        permissions = super().get_permissions()
        # Add the custom permission
        permissions.append(AlreadyExist(Restaurant))
        return permissions

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

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

    queryset = Dish.objects.select_related('restaurant__cuisine'
                                           ).prefetch_related('restaurant', 'category')
    serializer_class = DishSerializer
    # permission_classes = [ IsRestaurantOwnerOrReadOnly]
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
        return {'user': self.request.user}


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
            return {'user': self.request.user}
        return super().get_serializer_context()

    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated])
    def checkout(self, request, pk=None):
        '''example of the response from flutter
        : {"status":"success","message":"Hosted Link","data":{"link":"https://checkout-v2.dev-flutterwave.com/v3/hosted/pay/d142a38c632e6c92a2cc"}}
        and you get redirect to the link so the link doesn't expire
        '''

        cart = self.get_object()
        try:
            self.validate_cart(cart, self.get_serializer_context())

            processor = get_processor(cart.payment_method.payment_type)
            # redirect to this endpoint to confirm token then redirect from there to order endpoint
            response = processor.charge(cart)
            result = response.json()
            print('### payment link was processed{result}')
            if result['status'] == 'success':
                # provides link to the payment method on flutterwave and then we get redirected to our redirect url
                print(f"going for redirect link:{result['data']['link']}")
                return redirect(result['data']['link']) #Response(result, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Checkout failed {e}", "retry_url":request.get_full_path()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['GET'])
    def confirm_payment(self, request,pk=None):
        cart_id = request.query_params.get('c_id')
        encrypted_token = request.query_params.get('token')
        try:
            with transaction.atomic():
                payload = decrypt_token(token=encrypted_token)
                print(payload)

                # get cart to create order
                cart = Cart.objects.get(id=cart_id)
                if  payload['status']=='success' and payload['data']['total']==str(cart.total):
                    order = self.create_order_with_item_from_cart(cart=cart)

                    # delete the cart
                    # cart.delete()
                    return Response(
                        {'status': 'success', 'message': 'payment successful. Check your order',
                            'link_to_order': request.build_absolute_uri(reverse('orders-detail', kwargs={'pk': order.id}))
                        },
                        status=status.HTTP_200_OK)
                return Response(
                    {'status': 'failed', 'message': 'payment failed. Check your cart and checkout again. if you have been charged, contact support'},
                    status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Payment not completed: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def validate_cart(self, cart: Cart, context:dict):
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

    def create_order_with_item_from_cart(self, cart:Cart):

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
            dish_name= item.dish.name,
            unit_price= item.dish.unit_price,
            quantity= item.quantity,

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
        return { 'user': self.request.user}


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
    search_fields = ['delivery_type', 'is_active','base_fee']
    ordering_fields = ['is_active','base_fee']


class OrderViewSet(ModelViewSet):
    '''CRUD Order by only admin.'''
    serializer_class = OrderSerializer
    # permission_classes = [IsCustomerOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['status', 'payment_status','restaurant_name']
    ordering_fields = ['is_active','total','total']

    def get_queryset(self):
        return Order.objects.select_related('customer')
