import os
import requests
from django.shortcuts import redirect, HttpResponse
from django.utils.decorators import method_decorator 
from dotenv import load_dotenv

from django.db import transaction
from django.urls import reverse
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action,api_view
from rest_framework.exceptions import ValidationError

from apps.order.payment_processing import PaymentProcessor

from apps.order.documentation.schemas import ( 
    add_cart_docs, cart_item_destroy_docs , cart_item_retrieve_docs , order_docs,
    payment_method_docs
)
from .models import PaymentMethod, DeliveryMethod, Cart, CartItem, PaymentRecord, Order, OrderItem
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .serializers import (PaymentMethodSerializer, DeliveryMethodSerializer, CartSerializer,
                          AddCartItemSerializer, OrderSerializer
                          )
from .utils import decrypt_token, get_flutter_header
load_dotenv()
# Create your views here.


@api_view(['POST'])
# @csrf_exempt
def webhook(request):
    '''After successful payment flutterwave send a request here 
    sample :{
  "id": 8944267,
  "txRef": "6c644038-0579-4c4b-b4a7-0d14778747d2",
  "flwRef": "FLW-MOCK-39b3af2983712aa0666568b064e5be21",
  "orderRef": "URF_1745417323114_5909535",
  "paymentPlan": null,
  "paymentPage": null,
  "createdAt": "2025-04-23T14:08:43.000Z",
  "amount": 3100,
  "charged_amount": 3100,
  "status": "successful",
  "IP": "54.75.161.64",
  "currency": "NGN",
  "appfee": 43.4,
  "merchantfee": 0,
  "merchantbearsfee": 1,
  "charge_type": "normal",
  "customer": {
    "id": 3004322,
    "phone": "9090",
    "fullName": "Anonymous customer",
    "customertoken": null,
    "email": "oretammy@gmail.com",
    "createdAt": "2025-04-23T14:08:43.000Z",
    "updatedAt": "2025-04-23T14:08:43.000Z",
    "deletedAt": null,
    "AccountId": 2599090
  },
  "entity": {
    "card6": "553188",
    "card_last4": "2950",
    "card_country_iso": "NG",
    "createdAt": "2020-04-24T15:19:22.000Z"
  },
  "event.type": "CARD_TRANSACTION"
}
    

    '''
    secret_hash = os.getenv("FLW_SECRET_HASH")
    signature = request.headers.get("verifi-hash")
    if signature == None or (signature != secret_hash):
        # This request isn't from Flutterwave; discard
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    payload = request.body
    print(f'Here is the payment response from flutterwave {payload}')
    # It's a good idea to log all received events.
    # log(payload)
    # Do something (that doesn't take too long) with the payload
    return HttpResponse(status=200)



class PaymentMethodViewSet(ModelViewSet):
    '''CRUD payment method by only admin.'''
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['payment_type', 'is_active']
    ordering_fields = ['is_active']

for method_name, decorator_func in payment_method_docs.items():
    PaymentMethodViewSet = method_decorator(name=method_name, decorator=decorator_func)(PaymentMethodViewSet)


class DeliveryMethodViewSet(ModelViewSet):
    '''CRUD Delivery method by only admin.'''
    queryset = DeliveryMethod.objects.all()
    serializer_class = DeliveryMethodSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['delivery_type', 'is_active','base_fee']
    ordering_fields = ['is_active','base_fee']


class CartViewSet(ModelViewSet):
    '''include the Cart_id in the body to include other details,
    to add/increment item to/in a cart go the the cart/add-items '''

    serializer_class = CartSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Cart.objects.select_related('customer').filter(customer=self.request.user)

    def get_serializer_context(self):
        if self.request.user.is_authenticated:
            return {'user':self.request.user}
        return super().get_serializer_context()

    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated])
    def checkout(self, request, pk=None):
        '''example of the response from flutter
        {"status":"success","message":"Hosted Link","data":{"link":"https://checkout-v2.dev-flutterwave.com/v3/hosted/pay/d142a38c632e6c92a2cc"}}
        and you get redirect to the link so the link doesn't expire
        '''
        cart = self.get_object()
        try:
            self.validate_cart(cart, self.get_serializer_context())
            with transaction.atomic():
                result = PaymentProcessor().initialize_payment(cart)

                if result['status'] == 'success':
                    return Response(result, status=status.HTTP_200_OK) #redirect(result['data']['link'])
        except ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Checkout failed {e}", "retry_url":request.build_absolute_uri(reverse('carts-detail', kwargs={'pk': cart.id}))},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['GET'])
    def confirm_payment(self, request, pk=None):
        cart_id = self.kwargs['pk']
        encrypted_token = request.query_params.get('token')

        try:
            with transaction.atomic():
                token = decrypt_token(token=encrypted_token)
                tx_ref =token['data']['tx_ref']
                payment_record = PaymentRecord.objects.get(tx_ref=tx_ref, cart_id=cart_id)

                # use in production
                # if payment_record.payment_method == 'card':
                #     flw_verify_url = f"https://api.flutterwave.com/v3/transactions/{tx_ref}/verify"
                #     response = requests.get(url=flw_verify_url, headers=get_flutter_header())
                #     print(f'json:{str(response)}')

                #     if not response.json()['status'] == 'success':
                #         raise ValidationError('payment failed. if you have been charged, contact support else Retry!')

                cart = Cart.objects.get(id=cart_id)
                order = self.create_order_with_item_from_cart(cart=cart, transaction_reference=tx_ref)

                payment_record.delete()
                # cart.delete()
                return Response(
                    {'status': 'success', 'message': 'checkout successful. check your order',
                        'details':{'order_number': order.order_number, 'tx_ref':order.tx_ref },
                        'link_to_order': request.build_absolute_uri(reverse('orders-detail', kwargs={'pk': order.id}))
                    }, status=status.HTTP_200_OK)

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

    def create_order_with_item_from_cart(self, cart:Cart, transaction_reference):

        order = Order()
        order.customer = cart.customer
        order.restaurant_name = cart.restaurant.name
        order.tx_ref = transaction_reference
        order.status = 'confirmed'
        order.payment_status = 'paid' if cart.payment_method.payment_type == 'card' else 'pending'
        order.payment_method = cart.payment_method.payment_type
        order.delivery_method = cart.delivery_method.delivery_type
        order.subtotal = cart.sub_total
        order.delivery_fee = cart.delivery_method.base_fee
        order.total = cart.total
        address = cart.address
        order.address = f'{address.address_type}: {address.street_address}, {address.city}, {address.state},({address.postal_code} '
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

for method_name , decorator_func in add_cart_docs.items():
    AddCartItemsApiVIew = method_decorator(name=method_name, decorator=decorator_func) (AddCartItemsApiVIew)


@method_decorator(name='delete', decorator=cart_item_destroy_docs)
@method_decorator(name='get', decorator=cart_item_retrieve_docs)
class DeleteCartItemApiView(DestroyAPIView):
    '''
    User wants to completely delete a cart item
    '''

    serializer_class = AddCartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.select_related('cart').filter(id=self.kwargs['pk'], cart__customer=self.request.user).order_by('updated_at')

    def get_serializer_context(self):
        return { 'user': self.request.user}

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderViewSet(ModelViewSet):
    '''Read by all,modification by admin. After successful checkout order is created and cart is delete.'''

    http_method_names = ['get','options','patch']
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['status', 'payment_status','restaurant_name']
    ordering_fields = ['is_active','total','total']

    def get_queryset(self):
        order = Order.objects.select_related('customer')
        user = self.request.user
        if user.is_staff:
            return order
        return order.filter(customer=user)

for method_name,  decorator_func in order_docs.items():
    OrderViewSet = method_decorator(name=method_name, decorator=decorator_func)(OrderViewSet)
