from django.db.models import Count, Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from city.tasks import send_notification_email, create_comment_notification
from city.models import City, Location, Place, UserPlaceVisit

from .serializers import CitySerializer, PlaceSerializer, PlaceCommentSerializer, PlaceRatingSerializer


class CityView(APIView):
    """
    Comprehensive view for city-related operations
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CitySerializer

    def post(self, request):
        """
        Create a new city
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            city = serializer.save()

            request.user.cities.add(city)

            return Response(CitySerializer(city).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, city_id=None):
        """
        Retrieve a specific city or list of cities for the current user
        """
        if city_id:
            try:
                city = (
                    request.user.cities.prefetch_related(
                        Prefetch("places", queryset=Place.objects.all())
                    )
                    .annotate(places_count=Count("places"))
                    .get(id=city_id)
                )

                serializer = CitySerializer(city)
                return Response(serializer.data)

            except City.DoesNotExist:
                return Response(
                    {"detail": "City not found or not associated with user"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        cities = request.user.cities.annotate(places_count=Count("places"))
        serializer = self.serializer_class(cities, many=True)
        return Response(serializer.data)


class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PlaceCommentSerializer
    notifications = create_comment_notification  # Can just change this and send to email or phone number

    def post(self, request, place_id):
        """
        Create a new comment for a specific place
        """
        place = get_object_or_404(Place, id=place_id)
        data = request.data.copy()
        user = request.user
        data['user'] = user.id
        data['place'] = place.id
        serializer = self.serializer_class(data=data, context={"request": request})
        if serializer.is_valid():
            comment = serializer.save()
            place = comment.place
            place_creator = place.user

            self.notifications.delay(
                recipient_id=place_creator.id,
                sender_id=user.id,
                place_name=place.name,
                comment_text=comment.text
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlaceRatingView(APIView):
    """
    API endpoint for adding or updating a user's rating for a place
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PlaceRatingSerializer

    def post(self, request, place_id):
        """
        Add or update a rating for a specific place
        """
        place = get_object_or_404(Place, id=place_id)

        data = request.data.copy()
        data['user'] = request.user.id
        data['place'] = place.id

        serializer = self.serializer_class(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListPlacesView(ListAPIView):
    permissions = [IsAuthenticated]
    serializer_class = PlaceSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]

    filterset_fields = {
        "price": ["gte", "lte"],
        "average_rating": ["gte", "lte"],
    }

    ordering_fields = ["name", "price", "average_rating", "created_at"]

    search_fields = ["name", "description"]

    def get_queryset(self):
        """
        Override get_queryset to filter places by city ID from URL parameter
        """
        city_id = self.kwargs.get("city_id")
        return Place.objects.filter(city_id=city_id).select_related("location")


@method_decorator(csrf_exempt, name="dispatch")
class PlaceView(APIView):
    permissions = [IsAuthenticated]
    serializer_class = PlaceSerializer
    visited_class = UserPlaceVisit

    def post(self, request):
        """
        Create a new place
        """
        data = request.data.copy()
        print(data)
        required_fields = ["name", "price"]
        for field in required_fields:
            if field not in data:
                return Response(
                    {"error": f"{field} is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            city = get_object_or_404(City, id=data["city"])
            location, created = Location.objects.get_or_create(
                lat=data["latitude"], lng=data["longitude"]
            )
            serializer = self.serializer_class(data=data)

            if serializer.is_valid():
                place = serializer.save(city=city, location=location)

                return Response(
                    self.serializer_class(place).data, status=status.HTTP_201_CREATED
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, place_id):
        """
        Retrieve a specific place by its ID

        Includes:
        - Place details
        - Recent comments
        - Visit information
        """
        try:
            place = get_object_or_404(
                Place.objects.select_related("city", "location").prefetch_related(
                    "comments", "ratings", "visits"
                ),
                id=place_id,
            )

            serializer = self.serializer_class(place)
            response_data = serializer.data
            response_data.update(
                {
                    "recent_comments": [
                        {
                            "user": comment.user.username,
                            "text": comment.text,
                            "created_at": comment.created_at,
                        }
                        for comment in place.comments.all()[:5]
                    ],
                    "total_visits": place.visits.count(),
                    "total_comments": place.comments.count(),
                    "total_ratings": place.ratings.count(),
                }
            )

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, place_id):
        """
        Update an existing place

        Allows partial updates
        """
        try:
            place = get_object_or_404(Place, id=place_id)

            serializer = self.serializer_class(place, data=request.data, partial=True)

            if serializer.is_valid():
                updated_place = serializer.save()
                return Response(
                    self.serializer_class(updated_place).data, status=status.HTTP_200_OK
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, place_id):
        """
        Mark a place as visited for the authenticated user.
        """
        place = get_object_or_404(Place, id=place_id)

        notes = request.data.get('notes', '')

        visit, created = self.visited_class.mark_as_visited(user=request.user, place=place)

        if not created:
            visit.notes = notes or visit.notes
            visit.save()

        return Response(
            {
                "detail": f"Place '{place.name}' marked as visited.",
                "visited_at": visit.visited_at,
                "notes": visit.notes,
            },
            status=status.HTTP_200_OK,
        )
