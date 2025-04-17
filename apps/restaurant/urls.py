from django.urls import path,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register('profile/addresses',views.AddressViewSet,basename='addresses')

# only admin
router.register('payment-methods',views.PaymentMethodViewSet,basename='payment_methods')
router.register('delivery-methods',views.DeliveryMethodViewSet,basename='delivery_methods')
router.register('cuisine-types',views.CuisineViewSet,basename='cuisines')
router.register('categories',views.FoodCategoryViewSet,basename='categories')
# only admin end
router.register('restaurants',views.RestaurantViewSet,basename='restaurants')
router.register('dishes',views.DishViewSet,basename='dishes')
router.register('carts',views.CartViewSet,basename='carts')
router.register('orders',views.OrderViewSet,basename='orders')


urlpatterns = [
    path("carts/add-items/",views.AddCartItemsApiVIew.as_view(),name='cart_add_items'),


    path("", include(router.urls)),
]
