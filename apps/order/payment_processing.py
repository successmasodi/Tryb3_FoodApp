'''
Payment Processing System :
Supports : 
        ('card', 'Credit/Debit Card'),
        ('cod', 'Cash on Delivery'),
'''
import requests
import urllib.parse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .models import Cart, PaymentRecord, PaymentMethod
from .utils import encrypt_token, get_flutter_header

class PaymentProcessor:
    def initialize_payment(self, cart: Cart):
        '''start payment based on chosen payment method '''
        payment_method_type = cart.payment_method.payment_type
        cart_id = cart.id
        payment_record = PaymentRecord.get_or_create_for_cart(cart=cart)
        token = {'tx_ref':payment_record.tx_ref}
        redirect_url = f'http:/127.0.0.1:8000/api/v1/carts/{cart_id}/confirm_payment/?token={urllib.parse.quote(encrypt_token(payload=token))}'

        if not PaymentMethod.objects.filter(payment_type=payment_method_type, is_active=True).exists():
            raise ValidationError('Invalid payment method')

        if payment_method_type.lower() == 'cod':
            return {'status':'success', 'message':'cod payment', 'data': { 'link': redirect_url}}

        elif payment_method_type.lower() == 'card':
            flw_url = "https://api.flutterwave.com/v3/payments"
            header = get_flutter_header()

            body = {
                "tx_ref": payment_record.tx_ref,
                "amount": str(cart.total),
                "currency": "NGN",
                "redirect_url": redirect_url,
                'customer': {
                    "email": cart.customer.email,
                    "phone_number": cart.customer.phone_number,
                },
                "customizations": {
                    "title": "Tryb3 Food Delivery Payment"
                }
            }

            try:
                response = requests.post(url=flw_url, headers=header, json=body)

                if not response.status_code == status.HTTP_200_OK:
                    raise ValidationError(
                        {'status': 'error', 'message': 'invalid status code.', 'data': str(response)})
                return response.json()

            except Exception as e:
                raise ValidationError([{
                    'status': 'error',
                    'code': 'PAYMENT_FAILED',
                    'message': str(e),
                }]) from e
