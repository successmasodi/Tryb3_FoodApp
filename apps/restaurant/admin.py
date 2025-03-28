from django.contrib import admin
from django.db.models.aggregates import Count
from .models import Cuisine, Restaurant, Dish,FoodCategory

# Register your models here.


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    fields = ('name', 'slug', 'description', 'image')
    list_display = ('id', 'name', 'slug', 'restaurant_count', 'description')
    list_filter = ('name',)
    search_fields = ('name', 'description')
    show_facets = admin.ShowFacets.ALWAYS

    @admin.display(ordering='restaurant_count')
    def restaurant_count(self,cuisine):
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
    list_display = ('id', 'name', 'owner', 'cuisine','dish_count' ,'rating', 'is_featured', 'delivery_time', 'minimum_order')
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
    fields = ('restaurant', 'name', 'description', 'price', 'category', 'preparation_time', 
              'is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_available','is_featured', 'image')
    list_display = ('id', 'name', 'restaurant', 'price', 'category', 'is_available','is_featured')
    list_editable = ('name', 'price', 'is_available', 'category')
    list_filter = ('is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_available', 'is_featured', 'category')
    search_fields = ('name', 'description', 'price')
    list_select_related = ('restaurant', 'category')
    show_facets = admin.ShowFacets.ALWAYS

    @admin.display(ordering='name')
    def display_name(self, dish):
        return dish.name
