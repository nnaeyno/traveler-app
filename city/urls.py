from django.urls import path

from .views import CityView, CommentView, ListPlacesView, PlaceView

app_name = 'cities'

urlpatterns = [
    path("cities/", CityView.as_view(), name="city-list-create"),
    path("cities/<int:city_id>/", CityView.as_view(), name="city-detail"),
    path("comment/", CommentView.as_view(), name="comment"),
    path("places/", ListPlacesView.as_view(), name="places"),
    path("add-place", PlaceView.as_view(), name="add-place"),
    path("place/<int:place_id>/", PlaceView.as_view(), name="place"),
]
