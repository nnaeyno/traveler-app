from rest_framework import serializers

from city.models import City
from city.serializers import CitySerializer
from luggage.models import ChecklistItem, TravelDocument, Trip


class ChecklistItemSerializer(serializers.ModelSerializer):
    trip_id = serializers.PrimaryKeyRelatedField(
        queryset=Trip.objects.all(), source="trip", write_only=True
    )

    class Meta:
        model = ChecklistItem
        fields = ["id", "trip_id", "name", "is_packed"]
        read_only_fields = ["id"]

    def validate_trip_id(self, value):
        """
        Ensure the user has access to the trip.
        """
        if value.user != self.context["request"].user:
            raise serializers.ValidationError(
                "You don't have permission to add items to this trip."
            )
        return value


class TravelDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    trip_id = serializers.PrimaryKeyRelatedField(
        queryset=Trip.objects.all(), source="trip", write_only=True
    )

    class Meta:
        model = TravelDocument
        fields = ["id", "name", "file", "file_url", "trip_id", "uploaded_at"]
        read_only_fields = ["uploaded_at", "file_url"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and hasattr(obj.file, "url"):
            return request.build_absolute_uri(obj.file.url)
        return None

    def validate_trip_id(self, value):
        """
        Ensure the user has access to the trip.
        """
        if value.user != self.context["request"].user:
            raise serializers.ValidationError(
                "You don't have permission to add documents to this trip."
            )
        return value


class TripSerializer(serializers.ModelSerializer):
    checklist_items = ChecklistItemSerializer(many=True, read_only=True)
    documents = TravelDocumentSerializer(many=True, read_only=True)
    destination = CitySerializer(read_only=True)
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), write_only=True, source="destination"
    )

    class Meta:
        model = Trip
        fields = [
            "id",
            "name",
            "start_date",
            "end_date",
            "destination",
            "destination_id",
            "created_at",
            "checklist_items",
            "documents",
        ]
        read_only_fields = ["created_at"]

    def validate(self, data):
        """
        Check that start_date is before end_date.
        """
        if data["start_date"] > data["end_date"]:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )
        return data
