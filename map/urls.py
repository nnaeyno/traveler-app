from django.urls import path

from . import views
from .views import MapView

urlpatterns = [
    path("map/", MapView.as_view(), name="map-page"),
]