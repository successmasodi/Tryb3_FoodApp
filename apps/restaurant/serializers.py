from rest_framework import serializers
from .models import Cuisine, FoodCategory, Restaurant, Dish


class CuisineSerializer(serializers.ModelSerializer):
    restaurant_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cuisine
        fields = ('id', 'name', 'slug', 'description','restaurant_count' ,'image')
        read_only_fields = ['id', 'slug' ]


class SimpleCuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = ('id', 'name', 'slug',)
        read_only_fields = ['id', 'slug' ]


class FoodCategorySerializer(serializers.ModelSerializer):
    dish_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = FoodCategory
        fields = ('id', 'name', 'slug', 'dish_count', 'description')
        read_only_fields = ['id','slug']


class SimpleRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = (
            'id', 'name',  'rating',
        )
        read_only_fields = [
           'id', 'rating',
        ]

class SimpleDishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = (
            'id','name', 'description','price','category', 'image'
        )
        read_only_fields = ['id', 'restaurant']


class RestaurantSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    cuisine =SimpleCuisineSerializer(read_only=True)
    menu_count = serializers.IntegerField(source='dish_count',read_only=True)
    menu = SimpleDishSerializer(source='dishes', many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = (
            'id', 'owner', 'name', 'slug', 'description', 'address', 
            'cuisine', 'rating', 'delivery_time', 'minimum_order', 
            'image', 'cover_image','is_featured','menu_count' , 'menu', 'created_at', 'date_joined'
        )
        read_only_fields = [
            'id', 'slug', 'rating', 'created_at', 'updated_at', 'owner', 'dishes'
        ]


class DishSerializer(serializers.ModelSerializer):
    restaurant = SimpleRestaurantSerializer(read_only=True)
    categories = FoodCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Dish
        fields = (
            'id', 'restaurant', 'name', 'description', 'price', 
            'categories', 'preparation_time', 'is_vegetarian', 
            'is_vegan', 'is_gluten_free', 'is_available', 
            'image', 'created_at', 'updated_at'
        )
        read_only_fields = ['id','restaurant', 'created_at', 'updated_at']
