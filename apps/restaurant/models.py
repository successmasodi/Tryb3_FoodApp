from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone,text
from django.conf import settings
from uuid import uuid4
from .managers import (CuisineManager, FoodCategoryManager,RestaurantManager)


class Cuisine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='cuisine_images/',
        blank=True,
        null=True
    )
    objects = CuisineManager()

    class Meta:
        verbose_name = 'Cuisine'
        verbose_name_plural = 'Cuisines'
        ordering = ('name',)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = text.slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FoodCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    objects = FoodCategoryManager()

    class Meta:
        verbose_name = 'Food Category'
        verbose_name_plural = 'Food Categories'
        ordering = ('name',)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = text.slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='restaurant_owner'
    )
    name = models.CharField(max_length=255, unique=True, help_text='name of your restaurant must be unique to your business.')
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    address = models.TextField()
    cuisine = models.ForeignKey(
        Cuisine,
        on_delete=models.PROTECT,
        related_name='restaurants'
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    delivery_time = models.CharField(max_length=100,
        help_text="Average delivery time in minutes"
    )
    minimum_order = models.IntegerField(
        default=1
    )
    image = models.ImageField(
        upload_to='restaurant_images/',
        blank=True,
        null=True
    )
    cover_image = models.ImageField(
        upload_to='restaurant_cover_images/',
        blank=True,
        null=True
    )
    is_featured = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = RestaurantManager()

    class Meta:
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'
        ordering = ('-is_featured', '-rating', 'name')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['cuisine', 'is_featured']),
            models.Index(fields=['rating']),
        ]
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = text.slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.cuisine.name})"


class Dish(models.Model):
    #same as menu
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='dishes'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    category = models.ForeignKey(
        FoodCategory,
        on_delete=models.SET_NULL,
        related_name='dishes',
        null=True
    )
    preparation_time = models.IntegerField(
        help_text="Preparation time in minutes"
    )
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_available= models.BooleanField(default=True, help_text="a dish won't be available if it's out of stock")
    image = models.ImageField(
        upload_to='dish_images/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Dishes'
        ordering = ('is_featured', 'is_available', 'unit_price', 'name')
        indexes = [
            models.Index(fields=[ 'is_featured','is_available', 'unit_price', 'name',]),
        ]

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = text.slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Dish.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)


class Cart(models.Model):

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart #{self.id} - {self.customer.email}"


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE,related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def sub_total(self):
        return self.dish.unit_price * self.quantity

    class Meta:
        # dish shouldn't belong to a same cart twice instead the quantity should be increased
        unique_together = ('cart', 'dish')

    def __str__(self):
        return f"Cart item: {self.dish.name} x {self.quantity}"
    

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
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    delivery_address = models.TextField()
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status', 'payment_status']),
        ]

    @property
    def restaurants(self):
        return self.items.values_list('dish__restaurant', flat=True).distinct()


    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    def save(self, *args, **kwargs):
        if not self.order_number:
            date_part = timezone.now().strftime('%Y%m%d')
            last_order = Order.objects.order_by('-id').first() # last order
            sequence = (last_order.id + 1) if last_order else 1
            self.order_number = f"ORD-{date_part}-{sequence:06d}"

        if self.pk:
            if self.status == 'Delivered' and self.payment_status == 'Paid' and not self.delivered_at:
                self.delivered_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number}"

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, related_name='order_items')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)]) # this field must be set automatically
    special_requests = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Automatically set restaurant from dish if not specified
        if not self.restaurant_id:
            self.restaurant = self.dish.restaurant
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return self.dish.unit_price * self.quantity

    class Meta:
        unique_together = ('order', 'dish')

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"
