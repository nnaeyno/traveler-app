from django.urls import path

from .user_views import LoginView, RegisterView
from .views import MapView, PlaceView

app_name = "traveler"

urlpatterns = [
    path("map/", MapView.as_view(), name="map"),
    path("place/", PlaceView.as_view(), name="place"),
    path('login/', LoginView.as_view(), name='login'),
    path("signup/", RegisterView.as_view(), name="signup"),
]
