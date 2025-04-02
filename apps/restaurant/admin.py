from django.contrib import admin
from django.db.models.aggregates import Count
from .models import Address, Cuisine, Restaurant, Dish, FoodCategory,Cart, CartItem,PaymentMethod, Order, OrderItem

# Register your models here.


admin.site.register(Address)
admin.site.register(PaymentMethod)


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    fields = ('name', 'slug', 'description', 'image')
    list_display = ('id', 'name', 'slug', 'restaurant_count', 'description')
    list_filter = ('name',)
    search_fields = ('name', 'description')
    show_facets = admin.ShowFacets.ALWAYS

    @admin.display(ordering='restaurant_count')
    def restaurant_count(self, cuisine):
        return cuisine.restaurant_count


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    fields = ('name', 'slug', 'description')
    list_display = ('id', 'name', 'slug', 'dish_count')
    list_editable = ('name',)
    list_filter = ('name',)
    search_fields = ('name', 'description')
    show_facets = admin.ShowFacets.ALWAYS

    @admin.display(ordering='dish_count')
    def dish_count(self, obj):
        return obj.dish_count


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    fields = ('owner', 'name', 'slug', 'description', 'address', 'cuisine', 'rating', 'delivery_time',
              'minimum_order', 'image', 'cover_image', 'is_featured', 'date_joined')
    list_display = ('id', 'name', 'owner', 'cuisine', 'dish_count',
                    'rating', 'is_featured', 'delivery_time', 'minimum_order')
    list_editable = ('name', 'rating', 'is_featured', 'cuisine')
    list_filter = ('cuisine', 'is_featured', 'rating')
    search_fields = ('name', 'address', 'description')
    list_select_related = ('cuisine', 'owner')
    show_facets = admin.ShowFacets.ALWAYS
    date_hierarchy = 'date_joined'

    @admin.display(ordering='dish_count')
    def dish_count(self, obj):
        return obj.dish_count


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    fields = ('restaurant', 'name', 'description', 'unit_price', 'category', 'preparation_time',
              'is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_available', 'is_featured', 'image')
    list_display = ('id', 'name', 'restaurant', 'unit_price',
                    'category', 'is_available', 'is_featured')
    list_editable = ('name', 'unit_price', 'is_available','is_featured', 'category')
    list_filter = ('is_vegetarian', 'is_vegan', 'is_gluten_free',
                   'is_available', 'is_featured', 'category')
    search_fields = ('name', 'description', 'unit_price')
    list_select_related = ('restaurant', 'category')
    show_facets = admin.ShowFacets.ALWAYS

    @admin.display(ordering='name')
    def display_name(self, dish):
        return dish.name


admin.site.register(Cart)
admin.site.register(CartItem)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('sub_total',)
    fields = ('dish', 'restaurant', 'quantity', 'sub_total', 'special_requests')
    autocomplete_fields = ['dish', 'restaurant']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'payment_status', 'total', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'customer__email')
    readonly_fields = ('order_number', 'subtotal', 'total', 'created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('order_number', 'customer', 'status', 'payment_status')
        }),
        ('Financials', {
            'fields': ('subtotal', 'delivery_fee', 'tax', 'total')
        }),
        ('Delivery', {
            'fields': ('delivery_address', 'special_instructions', 'delivered_at')
        }),
    )
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'dish', 'quantity', 'sub_total')
    list_select_related = ('order', 'dish', 'restaurant')
    search_fields = ('order__order_number', 'dish__name')
    autocomplete_fields = ['order', 'dish', 'restaurant']

