from decimal import Decimal
from rest_framework import serializers
from apps.restaurant.models import Dish, Restaurant
from .models import PaymentMethod, DeliveryMethod, Cart, CartItem, Order, OrderItem


class PaymentMethodSerializer(serializers.ModelSerializer):
    '''for creating payment methods'''

    class Meta:
        model = PaymentMethod
        fields = ('id', 'payment_type', 'is_active')
        read_only_fields = ['id']


class DeliveryMethodSerializer(serializers.ModelSerializer):
    '''for creating delivery methods'''

    class Meta:
        model = DeliveryMethod
        fields = ('id', 'delivery_type', 'base_fee' , 'is_active', 'estimated_min_minutes', 'estimated_max_minutes')
        read_only_fields = ['id']


class BasicDishSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(source='unit_price', max_digits=10, decimal_places=2)

    class Meta:
        model = Dish
        fields = ('name', 'price')


class SimpleCartItemSerializer(serializers.ModelSerializer):
    dish = BasicDishSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'dish', 'quantity', 'sub_total',)
        read_only_fields = ['id', ]

    def get_sub_total(self,obj):
        return obj.sub_total


class CartSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user' in self.context:
            self.fields['address'].queryset = self.context['user'].addresses.all()

    cart_id = serializers.UUIDField(source='id')
    customer = serializers.StringRelatedField(read_only=True)
    restaurant = serializers.StringRelatedField(read_only=True)
    items = SimpleCartItemSerializer(read_only=True, many=True)
    items_total_price = serializers.SerializerMethodField()
    payment_method = serializers.SlugRelatedField(
        queryset=PaymentMethod.objects.filter(is_active=True), slug_field='payment_type'
        )
    delivery_method = serializers.SlugRelatedField(
        queryset=DeliveryMethod.objects.filter(is_active=True), slug_field='delivery_type'
        )
    delivery_fee = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            'cart_id', 'customer', 'restaurant','items', 'payment_method','address',
            'delivery_method','special_instructions', 'items_total_price','delivery_fee','total',
            'created_at', 'updated_at',
        )
        read_only_fields = ['cart_id']

    def get_items_total_price(self, obj) -> Decimal:
        return obj.sub_total

    def get_delivery_fee(self,obj:Cart) -> Decimal:
        if obj.delivery_method:
            return Decimal(obj.delivery_method.calculate_fee())
        return Decimal(00.00)
    
    def get_total(self,obj):
        return obj.total


class SimpleDishSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(source='unit_price', max_digits=10, decimal_places=2)

    class Meta:
        model = Dish
        fields = ('id', 'name', 'price', 'category', 'image')
        read_only_fields = ['id']


class AddCartItemSerializer(serializers.ModelSerializer):
    '''
    Add items to cart requires dish selection
    get the restaurant from the dish
    '''

    # shows only available dish
    cart = serializers.PrimaryKeyRelatedField(read_only=True)
    dish_id = serializers.PrimaryKeyRelatedField(
        queryset=Dish.objects.filter(is_available=True).order_by('-unit_price'),
        source='dish', write_only=True
    )
    dish = SimpleDishSerializer(read_only=True)
    restaurant = serializers.SerializerMethodField()

    def validate(self, attrs):
        dish = attrs.get('dish')
        if not dish and not Restaurant.objects.filter(id=dish.restaurant.id, is_active=True).first():
            raise serializers.ValidationError("Dish isn't available")
        return attrs

    class Meta:
        model = CartItem
        fields = ('id', 'cart',  'restaurant', 'dish_id', 'dish', 'quantity')
        read_only_fields = ('id',)
    
    def get_restaurant(self, obj):
        return obj.cart.restaurant.name

    def create(self, validated_data):
        user = self.context['user']
        dish = validated_data['dish']
        restaurant = dish.restaurant

        cart, created = Cart.objects.get_or_create(customer=user, restaurant=restaurant)

        if not created:  
            # Check if the item already exists in the cart
            existing_item = cart.items.filter(dish=dish).first()
            if existing_item:  # If the item already exists, increment the quantity
                existing_item.quantity += validated_data['quantity']
                existing_item.save()
                return existing_item
            else:
                new_cart_item = CartItem.objects.create(cart=cart, **validated_data)
                return new_cart_item
        
        return CartItem.objects.create(cart=cart, **validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'dish_name', 'unit_price', 'quantity')
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = serializers.StringRelatedField(read_only=True)
    delivered_at = serializers.DateTimeField(write_only=True)
    delivered = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'customer', 'restaurant_name', 'order_number', 'status', 'payment_status',
            'items', 'payment_method', 'delivery_method', 'address','special_instructions', 
            'subtotal', 'delivery_fee', 'total', 'created_at', 'updated_at','delivered_at','delivered'
        )
        read_only_fields = fields

    def get_delivered(self,obj):
        if obj.delivered_at:
            return obj.delivered_at.strftime("%Y-%m-%d %H:%M:%S")
        return 'yet to be delivered'

