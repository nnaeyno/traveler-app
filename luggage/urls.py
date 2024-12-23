from django.urls import path

from .views import add_checklist_item, create_trip

urlpatterns = [
    path("create/", create_trip, name="create_trip"),
    path("add_checklist/", add_checklist_item, name="add_checklist_item"),
]
