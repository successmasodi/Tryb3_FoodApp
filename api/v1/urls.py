from django.urls import path, include

urlpatterns = [
  path("",include('apps.restaurant.urls')),
  path("",include('apps.order.urls')),
    # path('flight/', include(('apps.flightapp.urls', 'flightapp'), namespace='flightapp')),
]
