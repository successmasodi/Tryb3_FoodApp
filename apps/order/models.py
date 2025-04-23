from decimal import Decimal
from uuid import uuid4
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.restaurant.models import Restaurant, Address, Dish


class PaymentMethod(models.Model):
    '''
    payment types are like categories
    '''
    PAYMENT_TYPES = [
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('cod', 'Cash on Delivery'),
        ('wallet', 'Digital Wallet')
    ]

    payment_type = models.CharField(max_length=20,unique=True, choices=PAYMENT_TYPES)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['is_active']
        indexes =[ models.Index(fields=('is_active',)) ]

    def __str__(self):
        return f"{self.payment_type}"


class DeliveryMethod(models.Model):
    METHOD_TYPES = [
        ('home', 'Home Delivery'),
        ('station', 'Pickup Station'),
        ('express', 'Express Delivery'),
        ('scheduled', 'Scheduled Delivery')
    ]

    delivery_type = models.CharField(max_length=20, choices=METHOD_TYPES, unique=True)
    description = models.TextField(blank=True)
    base_fee = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    distance_fee = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], default=0.00, help_text="Per kilometer charge"
    )
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.00)
    is_active = models.BooleanField(default=True)
    estimated_min_minutes = models.PositiveIntegerField(help_text="Minimum delivery time in minutes")
    estimated_max_minutes = models.PositiveIntegerField( help_text="Maximum delivery time in minutes")

    class Meta:
        ordering = ['base_fee']
    
    def __str__(self):
        return f"({self.get_delivery_type_display()} {self.base_fee})"

    def calculate_fee(self, distance_km=0, cart_total=0):
        """Calculate dynamic delivery fee"""
        fee = self.base_fee + (self.distance_fee * distance_km)
        return round(fee, 2)

        # Apply minimum order discount
        # if cart_total >= self.min_order_amount:
        #     return round(fee, 2)
        #     # fee = max(fee - 1.00, 0)  # $1 discount example
        # return None


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4,editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.SET_NULL, null=True, blank=True)
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart #{self.id} - {self.customer.email}"

    @property
    def sub_total(self):
        if self.items.exists():
            return sum(item.sub_total for item in self.items.all())
        return Decimal(00.00)

    @property
    def total(self):
        '''get total by adding the base fee and the total price of items in the cart'''
        if self.delivery_method:
            return Decimal(self.delivery_method.base_fee + self.sub_total)
        return Decimal(00.00)

    class Meta:
        indexes = [models.Index(fields=['customer']),]
        unique_together = ('customer', 'restaurant')


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def sub_total(self) -> int:
        return Decimal(self.dish.unit_price * self.quantity)

    @property
    def restaurant_name(self):
        return self.dish.restaurant.name

    class Meta:
        unique_together = ('cart', 'dish')
        ordering = ['-added_at']
        indexes = [models.Index(fields=['cart', 'dish']),]

    def __str__(self):
        return f"Cart item: {self.dish.name}({self.dish.unit_price}) x {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('confirmed', 'Confirmed'),
        ('ready', 'Ready for Delivery'), ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'), ('paid', 'Paid'),
        ('failed', 'Failed'), ('refunded', 'Refunded'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    restaurant_name = models.CharField(max_length=255)
    order_number = models.CharField(max_length=20, unique=True)
    tx_ref = models.CharField(max_length=36, unique=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20)
    delivery_method = models.CharField(max_length=20)
    address = models.TextField()
    special_instructions = models.TextField(blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status', 'payment_status']),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            date_part = timezone.now().strftime('%Y%m%d')
            last_order = Order.objects.order_by('-id').first()
            sequence = (last_order.id + 1) if last_order else 1
            self.order_number = f"ORD-{date_part}-{sequence:06d}"

        if self.pk:
            if self.status == 'Delivered' and self.payment_status == 'Paid' and not self.delivered_at:
                self.delivered_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.dish_name} x {self.quantity}"

    @property
    def sub_total(self):
        return Decimal(self.unit_price * self.quantity)
