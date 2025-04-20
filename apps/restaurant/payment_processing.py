'''
Payment Processing System :
Supports : 
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('cod', 'Cash on Delivery'),
        ('wallet', 'Digital Wallet')
'''

from abc import ABC, abstractmethod
import requests
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .models import Cart
from .utils import get_payment_auth_headers, generate_payment_data


def get_processor(method_type: str):
    '''pass the payment method. it will select its processor'''
    processors = {
        'card': CardProcessor(),
        'bank': BankTransferProcessor(),
        'cod': CODProcessor()
    }
    return processors[method_type]


class BasePaymentProcessor(ABC):
    '''Structure of payment processor every class that inherits this class
    must override the charge function'''
    @abstractmethod
    def charge(self, cart: Cart, **kwargs):
        pass


class CardProcessor(BasePaymentProcessor):
    def charge(self, cart: Cart, **kwargs):
        '''Logic for card processing Integration with flutterwave, 
        get the payment link and send the payment data tot he link'''

        flw_url = "https://api.flutterwave.com/v3/payments"
        payment_header = get_payment_auth_headers()
        body = generate_payment_data(cart=cart)

        try:
            print(f"request f body: {payment_header}")
            response = requests.post(url=flw_url, headers=payment_header, json=body)
            print(f"request from flutterwave body: {response.text}")

            if not response.status_code == status.HTTP_200_OK:
                raise ValidationError(
                    {'status': 'error', 'message': 'invalid status code'})
            return response

        except Exception as e:
            raise ValidationError([{
                'status': 'error',
                'message': 'Payment request failed. Please check your internet connection or try again later.',
                'details': str(e),
            }]) from e


class BankTransferProcessor(BasePaymentProcessor):
    def charge(self, cart: Cart, **kwargs):
        '''Logic for bank transfer processing'''
        # print(f"Payment through Bank Transfer{kwargs['cart'].__dict__}")
        return random.choice([True, False])


class CODProcessor(BasePaymentProcessor):
    def charge(self, cart: Cart, **kwargs):
        '''Logic for Cash on Delivery processing'''
        # print(f"Payment through cash on delivery{kwargs['cart'].__dict__}")
        return random.choice([True, False])


# 3. Token-Based Verification System

# # verification/models.py
# class Token(models.Model):
#     order = models.OneToOneField(
#         'orders.Order',
#         on_delete=models.CASCADE,
#         related_name='verification_token'
#     )
#     code = models.CharField(max_length=12, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()
#     is_used = models.BooleanField(default=False)

#     def is_valid(self):
#         return not self.is_used and self.expires_at > timezone.now()

#     def mark_used(self):
#         self.is_used = True
#         self.save()
