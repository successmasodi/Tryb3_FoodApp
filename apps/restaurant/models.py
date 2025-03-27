from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone,text
from django.conf import settings


class Cuisine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='cuisine_images/',
        blank=True,
        null=True
    )

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

    class Meta:
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'
        ordering = ('name',)
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
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
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
    is_available = models.BooleanField(default=True)
    image = models.ImageField(
        upload_to='dish_images/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Dishes'
        ordering = ('name',)
        indexes = [
            models.Index(fields=['restaurant', 'is_available']),
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
