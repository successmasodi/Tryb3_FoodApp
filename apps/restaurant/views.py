from django.shortcuts import render
from django.db.models import Count
from rest_framework.viewsets import ModelViewSet
from .models import Cuisine,FoodCategory
from .serializers import CuisineSerializer, FoodCategorySerializer
# Create your views here.


class CuisineViewSet(ModelViewSet):
  queryset = Cuisine.objects.annotate(restaurant_count=Count('restaurants'))
  serializer_class = CuisineSerializer


class FoodCategoryViewSet(ModelViewSet):
  queryset = FoodCategory.objects.annotate(dish_count=Count('dishes'))
  serializer_class = FoodCategorySerializer
