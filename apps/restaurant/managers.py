from django.db import models
from django.db.models.aggregates import Count


class CuisineManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(restaurant_count=Count('restaurants'))


class FoodCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(menu_count=Count('dishes'))


class RestaurantManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(menu_count=Count('dishes'))
