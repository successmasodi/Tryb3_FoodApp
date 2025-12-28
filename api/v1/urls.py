from django.urls import path, include

urlpatterns = [
  path("",include('apps.restaurant.urls'))
]
