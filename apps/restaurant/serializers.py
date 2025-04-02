from rest_framework import serializers
from .models import (
    Address, Cuisine, FoodCategory, Restaurant, Dish, Cart, CartItem, PaymentMethod
)


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Address
        fields = ('id', 'owner', 'street_address','address_type' ,'city', 'state', 'country', 'postal_code', 'is_default' )
        read_only_fields = ('id','user')


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
            'id', 'name','price', 'category', 'image'
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


class BasicDishSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(source='unit_price', max_digits=10, decimal_places=2)

    class Meta:
        model = Dish
        fields = (  'name','price')


class SimpleCartItemSerializer(serializers.ModelSerializer):
    dish = BasicDishSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()
    restaurant = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'dish', 'quantity','sub_total','restaurant')
        read_only_fields = ['id', ]

    def get_sub_total(self,obj):
        return obj.sub_total

    def get_restaurant(self,obj):
        return obj.restaurant_name


class CartSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    items = SimpleCartItemSerializer(read_only=True,many=True)
    total = serializers.SerializerMethodField()

    def validate(self, attrs):

        if Cart.objects.filter(customer=self.context['user']).exists():
            raise serializers.ValidationError("You can't create another cart!")
        return super().validate(attrs)

    class Meta:
        model = Cart
        fields = (
            'id', 'customer', 'items', 'created_at', 
            'updated_at', 'total'
        )
        read_only_fields = ['id']

    def get_total(self, obj):
        return obj.total


class AddCartItemSerializer(serializers.ModelSerializer):

    # show only available dish
    dish_id = serializers.PrimaryKeyRelatedField(
        queryset=Dish.objects.filter(is_available=True).order_by('-unit_price'),
        source='dish',
        write_only=True,
    )
    dish = SimpleDishSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'dish_id','dish', 'quantity')
        read_only_fields = ('id',)


    def create(self, validated_data):
        cart_pk = self.context['cart_pk']
        dish = validated_data['dish']

        cart_item, created = CartItem.objects.get_or_create(cart_id=cart_pk, dish=dish)

        if not created:
            cart_item.quantity += validated_data['quantity']
            cart_item.save()
        return cart_item


class UpdateCartItemSerializer(serializers.ModelSerializer):
    dish = SimpleDishSerializer(read_only=True)

    # update quantity in a cart
    class Meta:
        model = CartItem
        fields = ('quantity','dish')


class CartItemSerializer(serializers.ModelSerializer):
    dish = SimpleDishSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'cart', 'dish', 'quantity','sub_total')
        read_only_fields = ['id', 'cart']

    def get_sub_total(self,obj):
        return obj.sub_total


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ('id', 'name', 'type', 'is_active', 'processing_fee')
        read_only_fields = ['id']
