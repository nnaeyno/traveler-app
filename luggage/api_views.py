from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from luggage.models import Trip, ChecklistItem, TravelDocument
from luggage.serializers import TripSerializer, ChecklistItemSerializer, TravelDocumentSerializer


class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return trips for the currently authenticated user.
        """
        return Trip.objects.filter(user=self.request.user).select_related(
            'destination'
        ).prefetch_related('checklist_items', 'documents')

    def perform_create(self, serializer):
        """
        Set the user when creating a new trip.
        """
        serializer.save(user=self.request.user)


class ChecklistViewSet(viewsets.ModelViewSet):
    serializer_class = ChecklistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return checklist items for the authenticated user's trips.
        """
        return ChecklistItem.objects.filter(
            trip__user=self.request.user
        ).select_related('trip')

    def perform_create(self, serializer):
        """
        Create a new checklist item.
        """
        serializer.save()

    @action(detail=False, methods=['GET'])
    def by_trip(self, request):
        """
        Get checklist items for a specific trip.
        """
        trip_id = request.query_params.get('trip_id')
        if not trip_id:
            return Response(
                {"error": "trip_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        trip = get_object_or_404(Trip, id=trip_id, user=request.user)
        items = self.get_queryset().filter(trip=trip)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['PATCH'])
    def toggle_packed(self, request, pk=None):
        """
        Toggle the packed status of an item.
        """
        item = self.get_object()
        item.is_packed = not item.is_packed
        item.save()
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    def bulk_update(self, request):
        """
        Update multiple checklist items at once.
        """
        items = request.data.get('items', [])
        if not items:
            return Response(
                {"error": "No items provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_items = []
        for item_data in items:
            item = get_object_or_404(
                ChecklistItem,
                id=item_data.get('id'),
                trip__user=request.user
            )
            serializer = self.get_serializer(
                item,
                data=item_data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                updated_items.append(serializer.data)

        return Response(updated_items)


class TravelDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = TravelDocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        """
        Return documents for the authenticated user's trips.
        """
        return TravelDocument.objects.filter(
            user=self.request.user
        ).select_related('trip')

    def perform_create(self, serializer):
        """
        Set the user when creating a new document.
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def by_trip(self, request):
        """
        Get documents for a specific trip.
        """
        trip_id = request.query_params.get('trip_id')
        if not trip_id:
            return Response(
                {"error": "trip_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        trip = get_object_or_404(Trip, id=trip_id, user=request.user)
        documents = self.get_queryset().filter(trip=trip)
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to handle file deletion.
        """
        document = self.get_object()
        # Delete the actual file
        if document.file:
            document.file.delete(save=False)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['PUT'])
    def rename(self, request, pk=None):
        """
        Rename a document.
        """
        document = self.get_object()
        new_name = request.data.get('name')

        if not new_name:
            return Response(
                {"error": "New name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        document.name = new_name
        document.save()
        serializer = self.get_serializer(document)
        return Response(serializer.data)
