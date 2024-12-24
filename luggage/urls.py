from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import add_checklist_item, create_trip
from .api_views import TripViewSet, ChecklistViewSet, TravelDocumentViewSet

# trying different approaches
router = DefaultRouter()
router.register(r'trip', TripViewSet, basename='trip')
router.register(r'checklist', ChecklistViewSet, basename='checklist')
router.register(r'document', TravelDocumentViewSet, basename='document')

urlpatterns = [
    path("create/", create_trip, name="create_trip"),
    path("add_checklist/", add_checklist_item, name="add_checklist_item"),
    path('', include(router.urls)),
]
