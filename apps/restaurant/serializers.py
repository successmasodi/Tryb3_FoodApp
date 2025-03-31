from rest_framework import serializers
from .models import (
    Cuisine, FoodCategory, Restaurant, Dish, Cart, CartItem
)


class CuisineSerializer(serializers.ModelSerializer):
    restaurant_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cuisine
        fields = ('id', 'name', 'slug', 'description',
                  'restaurant_count', 'image')
        read_only_fields = ['id', 'slug']


class SimpleCuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = ('id', 'name', 'slug',)
        read_only_fields = ['id', 'slug']


class FoodCategorySerializer(serializers.ModelSerializer):
    dish_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = FoodCategory
        fields = ('id', 'name', 'slug', 'dish_count', 'description')
        read_only_fields = ['id', 'slug']


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
    price = serializers.DecimalField(source='unit_price', max_digits=10, decimal_places=2,)

    class Meta:
        model = Dish
        fields = (
            'id', 'name', 'description', 'price', 'category', 'image'
        )
        read_only_fields = ['id', 'restaurant']


class RestaurantSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    cuisine_type = SimpleCuisineSerializer(source='cuisine',read_only=True)
    cuisine = serializers.PrimaryKeyRelatedField(queryset=Cuisine.objects.all(), write_only=True)  # For input only    
    menu_count = serializers.IntegerField(source='dish_count', read_only=True)
    menu = SimpleDishSerializer(source='dishes', many=True, read_only=True)


    def validate(self, attrs):
        
        if Restaurant.objects.only('id').filter(owner=self.context['user']).exists():
            raise serializers.ValidationError('You own a restaurant already.')
        return super().validate(attrs)

    class Meta:
        model = Restaurant
        fields = (
            'id', 'owner', 'name', 'slug', 'description', 'address','cuisine_type',
            'cuisine', 'rating', 'delivery_time', 'minimum_order',
            'image', 'cover_image', 'is_featured', 'menu_count', 'menu','date_joined'
        )
        read_only_fields = [ 'id', 'slug', 'rating', 'owner']

class DishSerializer(serializers.ModelSerializer):
    restaurant = SimpleRestaurantSerializer(read_only=True)
    category = FoodCategorySerializer(read_only=True)
    food_category = serializers.SlugRelatedField(
        source='category',
        queryset=FoodCategory.objects.all(),
        slug_field='name',
        write_only=True
    )
    price = serializers.DecimalField(source='unit_price', max_digits=10, decimal_places=2,)

    def validate(self, attrs):
        '''A user must have a restaurant before creating dishes.'''

        if not Restaurant.objects.filter(owner=self.context['user']).exists():
            raise serializers.ValidationError(
                'You should own a restaurant before creating a dish.'
            )
        return attrs

    class Meta:
        model = Dish
        fields = (
            'id', 'restaurant', 'name', 'description', 'price',
            'category', 'food_category','preparation_time', 'is_vegetarian',
            'is_vegan', 'is_gluten_free', 'is_available',
            'image', 'created_at', 'updated_at'
        )
        read_only_fields = ['id', 'restaurant', 'created_at', 'updated_at']


class CartSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    items = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = (
            'id', 'customer', 'items', 'created_at'
        )
        read_only_fields = ['id']




class SimpleCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ( 'id', 'created_at')
        read_only_fields = ['id']



class CartItemSerializer(serializers.ModelSerializer):
    cart = SimpleCartSerializer(read_only=True)
    dish = SimpleDishSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()
    restaurant = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'cart', 'dish', 'quantity','sub_total','restaurant')
        read_only_fields = ['id', 'cart']

    def get_sub_total(self):
        return self.sub_total()
    
    def get_restaurant(self):
        return self.restaurant
