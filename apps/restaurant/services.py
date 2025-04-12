
### . Enhanced Order Processing Flow

# orders/services.py
from django.db import transaction
from .payment_processing import get_processor
import secrets
from .models import Order
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from rest_framework.exceptions import ValidationError



def generate_confirm_token(cart):
    """
    Generates a token for payment confirmation.
    """
    refresh = RefreshToken.for_user(cart.customer)
    refresh['cart_id'] = cart.id
    refresh['exp'] = timezone.now() + timedelta(hours=20)
    return str(refresh.access_token)

class OrderService:
    @classmethod
    @transaction.atomic
    def process_checkout(cls, cart, payment_token=None):
        """
        \checkout flow:
        1. Process payment
        2. Handle success/failure
        3. Create order record
        """
        # 2. Process payment

        payment_result = cls.process_payment(
            cart=cart,
            method=cart.payment_method,
            token=payment_token
        )
        
        # 4. Handle results
        if payment_result.success:
            cls.handle_successful_payment(cart, payment_result)
            return cart, payment_result
        else:
            raise ValidationError('Failed Checkout process')
  
    @classmethod
    def process_payment(cls, cart, method, token=None):
        """Handle different payment methods"""
        processor = get_processor(method) # e.g method cod return CODProcessor()
        return processor.charge(
            amount=cart.total,
            order_ref=None,
            payment_token=token,
            customer=cart.customer
        )


    @classmethod
    def handle_successful_payment(cls, cart, order_number):
        """Complete order processing"""

        #Create order (price snapshot)
        order = cls.create_order_from_cart(cart)

        order.status = 'confirmed'
        order.payment_status = 'paid'
        order.order_number = order_number
        order.save()
        
        # Clean up cart
        order.customer.cart.items.all().delete()
        
        # Send confirmation
        # cls.send_order_confirmation(order)

    #     # Generate delivery token
    #     cls.generate_delivery_token(order)

    # @classmethod
    # def generate_delivery_token(cls, order):
    #     """Create verification token for order"""
    #     token = Token.objects.create(
    #         order=order,
    #         code=secrets.token_urlsafe(8).upper(),
    #         expires_at=timezone.now() + timedelta(days=1)
    #     )
    #     return token
