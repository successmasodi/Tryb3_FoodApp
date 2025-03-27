from django.contrib import admin
from .models import Cuisine, Restaurant, Dish,FoodCategory

# Register your models here.


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    fields = ('name', 'slug', 'description', 'image')
    list_display = ('id', 'name', 'slug', 'get_restaurant_count', 'description')
    list_filter = ('name',)
    search_fields = ('name', 'description')
    # list_select_related = ('restaurants',)  # Ensuring restaurant count optimization
    show_facets = admin.ShowFacets.ALWAYS

    @admin.display(ordering='name')
    def get_restaurant_count(self, cuisine):
        return cuisine.get_restaurant_count()

@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    fields = ('name', 'slug', 'description')
    list_display = ('id', 'name', 'slug', 'description')
    list_filter = ('name',)
    search_fields = ('name', 'description')
    show_facets = admin.ShowFacets.ALWAYS


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    fields = ('owner', 'name', 'slug', 'description', 'address', 'cuisine', 'rating', 'delivery_time', 
              'minimum_order', 'image', 'cover_image', 'is_featured', 'date_joined')
    list_display = ('id', 'name', 'owner', 'cuisine', 'rating', 'is_featured', 'delivery_time', 'minimum_order')
    list_editable = ('name', 'rating', 'is_featured', 'cuisine')
    list_filter = ('cuisine', 'is_featured', 'rating')
    search_fields = ('name', 'address', 'description')
    list_select_related = ('cuisine', 'owner')
    show_facets = admin.ShowFacets.ALWAYS
    date_hierarchy = 'date_joined'

    @admin.display(ordering='rating')
    def display_rating(self, restaurant):
        return restaurant.rating


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    fields = ('restaurant', 'name', 'description', 'price', 'category', 'preparation_time', 
              'is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_available', 'image', 'created_at', 'updated_at')
    list_display = ('id', 'name', 'restaurant', 'price', 'category', 'is_available', 'preparation_time')
    list_editable = ('name', 'price', 'is_available', 'category')
    list_filter = ('is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_available', 'category')
    search_fields = ('name', 'description', 'price')
    list_select_related = ('restaurant', 'category')  # Optimizing related queries
    show_facets = admin.ShowFacets.ALWAYS
    date_hierarchy = 'created_at'

    @admin.display(ordering='name')
    def display_name(self, dish):
        return dish.name
