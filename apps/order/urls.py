from django.urls import path,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

# only admin
router.register('payment-methods', views.PaymentMethodViewSet, basename='payment_methods')
router.register('delivery-methods', views.DeliveryMethodViewSet, basename='delivery_methods')


router.register('carts', views.CartViewSet, basename='carts')
router.register('orders', views.OrderViewSet, basename='orders')


urlpatterns = [
    path("carts/add-items/", views.AddCartItemsApiVIew.as_view(), name='cart_add_items'),
    path('flutterwave-payment-webhook/', views.webhook, name='flutter-webhook'),
    path("", include(router.urls)),
]
