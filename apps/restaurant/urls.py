from django.urls import path,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register('cuisines',views.CuisineViewSet,basename='cuisines')
router.register('categories',views.FoodCategoryViewSet,basename='categories')

urlpatterns = [
    path("", include(router.urls)),
]
