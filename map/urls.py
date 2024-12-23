from django.urls import path

from .views import MapView, PlaceView, Login, SignUp

app_name = "traveler"

urlpatterns = [
    path("map/", MapView.as_view(), name="map"),
    path("place/", PlaceView.as_view(), name="place"),
    path("login/", Login.as_view(), name="login"),
    path("signup/", SignUp.as_view(), name="signup"),
]
