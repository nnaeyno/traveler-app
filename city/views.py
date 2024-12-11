from city.models import City, Place
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView, CreateAPIView
from django.db.models import Count, Prefetch
from .serializers import CitySerializer


class CityView(APIView):
    """
    Comprehensive view for city-related operations
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CitySerializer

    def post(self, request):
        """
        Create a new city
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            city = serializer.save()

            request.user.cities.add(city)

            return Response(
                CitySerializer(city).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request, city_id=None):
        """
        Retrieve a specific city or list of cities for the current user
        """
        if city_id:
            try:
                city = request.user.cities.prefetch_related(
                    Prefetch('places', queryset=Place.objects.all()[:5])
                ).annotate(
                    places_count=Count('places')
                ).get(id=city_id)

                serializer = CitySerializer(city)
                return Response(serializer.data)

            except City.DoesNotExist:
                return Response(
                    {'detail': 'City not found or not associated with user'},
                    status=status.HTTP_404_NOT_FOUND
                )

        cities = request.user.cities.annotate(places_count=Count('places'))
        serializer = self.serializer_class(cities, many=True)
        return Response(serializer.data)


class CommentView(APIView):
    pass


class ListPlacesView(ListAPIView):
    pass


class PlaceView(APIView):
    pass
