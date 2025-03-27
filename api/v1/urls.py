from django.urls import path, include

urlpatterns = [
  path("",include('apps.restaurant.urls'))
    # path('flight/', include(('apps.flightapp.urls', 'flightapp'), namespace='flightapp')),
    # path('route/', include(('apps.route.urls', 'route'), namespace='route')),
]
