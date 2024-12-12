from django.urls import path

from .views import CityView, CommentView, ListPlacesView, PlaceView

app_name = 'cities'

urlpatterns = [
    path("cities/", CityView.as_view(), name="city-list-create"),
    path("cities/<int:city_id>/", CityView.as_view(), name="city-detail"),
    path("comment/", CommentView.as_view(), name="comment"),
    path('cities/<int:city_id>/places/', ListPlacesView.as_view(), name='places-by-city'),
    path('places/', PlaceView.as_view(), name='add-place'),
    path('places/<int:place_id>/', PlaceView.as_view(), name='place-detail'),
]
