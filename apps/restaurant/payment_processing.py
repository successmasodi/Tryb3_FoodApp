'''
Payment Processing System :
Supports : 
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('cod', 'Cash on Delivery'),
        ('wallet', 'Digital Wallet')
'''

from abc import ABC, abstractmethod
import random

def get_processor(method_type:str):
    '''pass the payment method.it will select its processor'''
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
    def charge(self, amount, order_ref, **kwargs):
        pass

class CardProcessor(BasePaymentProcessor):
    def charge(self, amount, order_ref, **kwargs):
        '''Logic for card processing Integration with Stripe/Paystack/etc'''
        print(f"Payment through card {kwargs['cart'].__dict__}")
        return random.choice([True,False])

class BankTransferProcessor(BasePaymentProcessor):
    def charge(self, amount, order_ref, **kwargs):
        '''Logic for bank transfer processing'''
        print(f"Payment through Bank Transfer{kwargs['cart'].__dict__}")
        return random.choice([True,False])
        

class CODProcessor(BasePaymentProcessor):
    def charge(self, amount, order_ref, **kwargs):
        '''Logic for Cash on Delivery processing'''
        print(f"Payment through cash on delivery{kwargs['cart'].__dict__}")
        return random.choice([True,False])




### 3. Token-Based Verification System

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

