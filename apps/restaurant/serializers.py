from rest_framework import serializers
from .models import (
    Address, Cuisine, FoodCategory, Restaurant, Dish
)



class AddressSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()

    class Meta:
        model = Address
        fields = ('id', 'owner', 'street_address', 'address_type',
                  'city', 'state', 'country', 'postal_code', 'is_default')
        read_only_fields = ('id', 'user')


class SimpleCuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = ('id', 'name', 'slug',)
        read_only_fields = ('id', 'slug')


class CuisineSerializer(serializers.ModelSerializer):
    restaurant_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cuisine
        fields = ('id', 'name', 'slug', 'description',
                  'restaurant_count', 'image')
        read_only_fields = ('id', 'slug')


class FoodCategorySerializer(serializers.ModelSerializer):
    menu_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = FoodCategory
        fields = ('id', 'name', 'slug', 'menu_count', 'description')
        read_only_fields = ('id', 'slug')


class SimpleRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'name',  'rating')
        read_only_fields = ('id', 'rating')


class SimpleDishSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(source='unit_price', max_digits=10, decimal_places=2)

    class Meta:
        model = Dish
        ref_name = 'MenuSerializer'
        fields = ('id', 'name', 'price', 'category', 'image')
        read_only_fields = ('id',)


class RestaurantSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    cuisine_type = SimpleCuisineSerializer(source='cuisine', read_only=True)
    cuisine = serializers.PrimaryKeyRelatedField(
        queryset=Cuisine.objects.all(), write_only=True)
    menu_count = serializers.SerializerMethodField()
    menu = SimpleDishSerializer(source='dishes', many=True, read_only=True)

    def validate(self, attrs):
        if Restaurant.objects.only('id').filter(owner=self.context['user']).exists():
            raise serializers.ValidationError('You own a restaurant already.')
        return super().validate(attrs)

    def get_menu_count(self,obj):
        return obj.menu_count

    class Meta:
        model = Restaurant
        fields = (
            'id', 'owner', 'name', 'slug', 'description', 'address', 'cuisine_type',
            'cuisine', 'rating', 'delivery_time', 'minimum_order',
            'image', 'cover_image', 'is_featured', 'menu_count', 'menu', 'date_joined'
        )
        read_only_fields = ('id', 'rating', 'owner', 'menu_count')


class DishSerializer(serializers.ModelSerializer):
    restaurant = SimpleRestaurantSerializer(read_only=True)
    category = FoodCategorySerializer(read_only=True)
    food_category = serializers.SlugRelatedField(
        source='category', queryset=FoodCategory.objects.all(),
        slug_field='name', write_only=True
    )
    price = serializers.DecimalField(
        source='unit_price', max_digits=10, decimal_places=2,)

    def validate(self, attrs):
        '''A user must have a restaurant before creating dishes.'''

        if not Restaurant.objects.filter(owner=self.context['user']).exists():
            raise serializers.ValidationError('You should own a restaurant before creating a dish.')
        return attrs

    class Meta:
        model = Dish
        fields = (
            'id', 'restaurant', 'name', 'slug', 'image', 'description', 'price',
            'category', 'food_category', 'preparation_time', 'is_vegetarian',
            'is_vegan', 'is_gluten_free', 'is_available',
            'image', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'restaurant', 'created_at', 'updated_at')
