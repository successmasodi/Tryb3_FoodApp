from django.contrib import admin
from .models import (
    Address, Cuisine, Restaurant, Dish, FoodCategory,
    )

# Register your models here.
admin.site.register(Address)


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
    list_display = ('id', 'name', 'slug', 'menu_count')
    list_editable = ('name',)
    list_filter = ('name',)
    search_fields = ('name', 'description')
    show_facets = admin.ShowFacets.ALWAYS

    @admin.display(ordering='menu_count')
    def menu_count(self, obj):
        return obj.menu_count


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    fields = ('owner', 'name', 'slug', 'description', 'address', 'cuisine', 'rating', 'delivery_time',
              'minimum_order', 'image', 'cover_image', 'is_featured', 'is_active', 'date_joined')
    list_display = ('id', 'name', 'owner', 'cuisine', 'menu_count',
                    'rating', 'is_featured', 'is_active', 'delivery_time', 'minimum_order')
    list_editable = ('name', 'rating', 'is_featured', 'cuisine')
    list_filter = ('cuisine', 'is_featured', 'rating')
    search_fields = ('name', 'address', 'description')
    list_select_related = ('cuisine', 'owner')
    show_facets = admin.ShowFacets.ALWAYS
    date_hierarchy = 'date_joined'

    @admin.display(ordering='menu_count')
    def menu_count(self, obj):
        return obj.menu_count


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    fields = ('restaurant', 'name', 'description', 'unit_price', 'category', 'preparation_time',
              'is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_available', 'is_featured', 'image')
    list_display = ('id', 'name', 'restaurant', 'unit_price',
                    'category', 'is_available', 'is_featured')
    list_editable = ('name', 'unit_price', 'is_available',
                     'is_featured', 'category')
    list_filter = ('is_vegetarian', 'is_vegan', 'is_gluten_free',
                   'is_available', 'is_featured', 'category')
    search_fields = ('name', 'description', 'unit_price')
    list_select_related = ('restaurant', 'category')
    show_facets = admin.ShowFacets.ALWAYS

    @admin.display(ordering='name')
    def display_name(self, dish):
        return dish.name


