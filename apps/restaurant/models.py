''''
Models that requires name and slug should inherit the SLug model mixin.
This model handles generic slug unique slug field generation 
'''

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone, text
from django.conf import settings
from .managers import (CuisineManager, FoodCategoryManager, RestaurantManager)


class SlugModelMixin(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        abstract = True

    def generate_unique_slug(self):
        base_slug = text.slugify(self.name)
        slug = base_slug
        ModelClass = self.__class__

        existing_slugs = ModelClass.objects.filter(slug__startswith=base_slug).values_list('slug', flat=True)
        if slug not in existing_slugs:
            return slug

        count = 1
        while slug in existing_slugs:
            slug = f'{base_slug}-{count}'
            count += 1
        return slug

    def save(self, *args, **kwargs):
        generate_slug = not self.slug

        if self.pk:
            try:
                obj = self.__class__.objects.get(pk=self.pk)
                if obj.name != self.name:
                    generate_slug = True
            except self.__class__.DoesNotExist:
                generate_slug = True

        if generate_slug:
            self.slug = self.generate_unique_slug()

        super().save(*args, **kwargs)


class Address(models.Model):

    ADDRESS_TYPES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    street_address = models.CharField(max_length=255)
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPES, default='home')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address_type} : {self.owner.email} - {self.street_address}, {self.city}, {self.state},({self.postal_code})"

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(customer=self.owner, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Cuisine(SlugModelMixin):

    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='cuisine_images/', blank=True, null=True)
    objects = CuisineManager()

    class Meta:
        verbose_name = 'Cuisine'
        verbose_name_plural = 'Cuisines'
        ordering = ('name',)

    def __str__(self):
        return self.name


class FoodCategory(SlugModelMixin):


    description = models.TextField(blank=True)
    objects = FoodCategoryManager()

    class Meta:
        verbose_name = 'Food Category'
        verbose_name_plural = 'Food Categories'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Restaurant(SlugModelMixin):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='restaurant_owner')
    name = models.CharField(max_length=255, unique=True, help_text='name of your restaurant must be unique to your business.')
    description = models.TextField(blank=True)
    address = models.TextField()
    cuisine = models.ForeignKey(Cuisine, on_delete=models.PROTECT, related_name='restaurants')
    rating = models.DecimalField(
        max_digits=3, decimal_places=1, default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    delivery_time = models.CharField(max_length=100,help_text="Average delivery time in minutes")
    minimum_order = models.IntegerField(default=1)
    image = models.ImageField(upload_to='restaurant_images/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='restaurant_cover_images/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = RestaurantManager()

    class Meta:
        ordering = ('-is_featured', '-rating', 'name')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['cuisine', 'is_featured']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.name} ({self.cuisine.name})"


class Dish(SlugModelMixin):
    #same as menu
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='dishes')
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    category = models.ForeignKey(FoodCategory, on_delete=models.PROTECT, related_name='dishes')
    preparation_time = models.IntegerField(help_text="Preparation time in minutes")
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_available= models.BooleanField(default=True, help_text="a dish won't be available if it's out of stock")
    image = models.ImageField(upload_to='dish_images/',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Dishes'
        ordering = ('is_featured', 'is_available', 'unit_price', 'name')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=[ 'is_featured','is_available', 'unit_price', 'name',]),
        ]

    def __str__(self):
        return f"{self.name} from {self.restaurant.name} - N{self.unit_price}"
