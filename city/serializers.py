from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from city.models import City, Place, PlaceRating, UserPlaceVisit


def get_comments_count(obj):
    """
    Get the total number of comments for this place
    """
    return obj.comments.count()


def get_location_details(obj):
    """
    Retrieve additional location information
    """
    return {
        "latitude": obj.location.latitude,
        "longitude": obj.location.longitude,
    }


class PlaceSerializer(serializers.ModelSerializer):
    """
    Serializer for Place model with comprehensive field handling
    """

    city_name = serializers.CharField(source="city.name", read_only=True)
    location_details = serializers.SerializerMethodField()

    average_rating = serializers.FloatField(read_only=True)
    total_ratings = serializers.IntegerField(read_only=True)

    photo = serializers.ImageField(
        required=False,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "gif"])],
    )

    user_rating = serializers.SerializerMethodField()
    user_visited = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = [
            "id",
            "name",
            "description",
            "city",
            "city_name",
            "location",
            "location_details",
            "price",
            "photo",
            "average_rating",
            "total_ratings",
            "user_rating",
            "user_visited",
            "comments_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "average_rating",
            "total_ratings",
            "created_at",
            "updated_at",
        ]

    def get_user_rating(self, obj):
        """
        Get the current user's rating for this place
        """
        user = self.context.get("request").user
        if not user.is_authenticated:
            return None

        try:
            rating = PlaceRating.objects.get(user=user, place=obj)
            return rating.rating
        except PlaceRating.DoesNotExist:
            return None

    def get_user_visited(self, obj):
        """
        Check if the current user has visited this place
        """
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False

        return UserPlaceVisit.objects.filter(user=user, place=obj).exists()

    def create(self, validated_data):
        """
        Custom create method with additional processing
        """
        city = validated_data.pop("city", None)
        location = validated_data.pop("location", None)

        place = Place.objects.create(city=city, location=location, **validated_data)

        return place

    def update(self, instance, validated_data):
        """
        Custom update method with specific update logic
        """
        if "photo" in validated_data:
            if instance.photo:
                instance.photo.delete()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CitySerializer(serializers.ModelSerializer):
    places_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = City
        fields = ["id", "name", "places_count"]


class CityDetailSerializer(CitySerializer):
    recent_places = PlaceSerializer(many=True, read_only=True)

    class Meta(CitySerializer.Meta):
        fields = CitySerializer.Meta.fields + ["recent_places"]
