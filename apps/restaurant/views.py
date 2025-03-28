from django.db.models import Count
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cuisine, FoodCategory, Restaurant, Dish
from .serializers import CuisineSerializer, FoodCategorySerializer, RestaurantSerializer, DishSerializer


# Create your views here.
class CuisineViewSet(ModelViewSet):
    '''View for cuisine. search by name, ordered by name and 
    restaurant_count: number of restaurant under the cuisine'''

    queryset = Cuisine.objects.all()
    serializer_class = CuisineSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'restaurant_count']


class FoodCategoryViewSet(ModelViewSet):
    '''View for Food category. search by name, ordered by name and 
    dish_count: number of dishes under the category'''

    queryset = FoodCategory.objects.all()
    serializer_class = FoodCategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'dish_count']


class RestaurantViewSet(ModelViewSet):
    '''View for Restaurant. 
    search by:
        'name', 'address', 'cuisine name', 'dishes name'
    ordered by: 
        '-is_featured', '-rating', 'name
    filter by:
        'is featured',  'rating', 'cuisine name', 'owner', 'dish_count',
    
    dish_count: number of dishes by the restaurant
    '''

    queryset = Restaurant.objects.select_related('owner', 'cuisine')\
        .prefetch_related('dishes')
    serializer_class = RestaurantSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = [
        'name', 'address', 'cuisine__name', 'dishes__name'
    ]
    filterset_fields = [
        'is_featured', 'rating', 'cuisine__name','dish_count',
        'owner', 
    ]


class DishViewSet(ModelViewSet):
    '''View for  Dish. 
    search by:
        'name', 'restaurant name', 'category name'
    ordered by: 
        'is_featured', 'is_available', 'price', 'name'
    filter by:
        'is_featured', 'restaurant', 'category',
        'is_vegetarian', 'is_vegan',
        'is_gluten_free',  'is_available'
    '''
    queryset = Dish.objects.select_related(
        'restaurant', 'restaurant__cuisine'
    ).prefetch_related('category')
    serializer_class = DishSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = [
        'name', 'restaurant__name', 'category__name'
    ]
    filterset_fields = [
        'is_featured', 'restaurant', 'category',
        'is_vegetarian', 'is_vegan',
        'is_gluten_free',  'is_available'
    ]
