from django.urls import path,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register('profile/addresses',views.AddressViewSet,basename='addresses')

# only admin
router.register('cuisine-types',views.CuisineViewSet,basename='cuisines')
router.register('categories',views.FoodCategoryViewSet,basename='categories')
# only admin end
router.register('restaurants',views.RestaurantViewSet,basename='restaurants')
router.register('dishes',views.DishViewSet,basename='dishes')

urlpatterns = [
    path("", include(router.urls)),
]
