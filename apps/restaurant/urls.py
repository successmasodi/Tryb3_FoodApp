from django.urls import path,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register('cuisine_types',views.CuisineViewSet,basename='cuisines')
router.register('categories',views.FoodCategoryViewSet,basename='categories')
router.register('restaurants',views.RestaurantViewSet,basename='Restaurants')
router.register('dishes',views.DishViewSet,basename='dishes')
router.register('carts',views.CartViewSet,basename='carts')

urlpatterns = [
    path("", include(router.urls)),
]
