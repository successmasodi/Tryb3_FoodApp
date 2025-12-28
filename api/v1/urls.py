from django.urls import path, include

urlpatterns = [
<<<<<<< HEAD
  path("",include('apps.restaurant.urls'))
=======
  path("",include('apps.restaurant.urls')),
  path("",include('apps.order.urls')),
>>>>>>> f753283344a55e4e45cb1213f645c638645f541f
]
