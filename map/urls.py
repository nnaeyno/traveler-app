from django.urls import path

from .views import MapView, PlaceView
from .user_views import LoginView, RegisterView

app_name = "traveler"

urlpatterns = [
    path("map/", MapView.as_view(), name="map"),
    path("place/", PlaceView.as_view(), name="place"),
    path("login/", LoginView.as_view(), name="login"),
    path("signup/", RegisterView.as_view(), name="signup"),
]
