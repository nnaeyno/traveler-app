from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from city.models import City
from city.serializers import CitySerializer

from .models import User
from .serializers import (
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)
from .service import UserUpdateService
from .validators import PasswordValidator, UniqueFieldValidator


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Registration successful",
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            identifier = serializer.validated_data["identifier"]
            password = serializer.validated_data["password"]

            try:
                if "@" in identifier:
                    user = User.objects.get(email=identifier)
                else:
                    user = User.objects.get(username=identifier)

                # Check password
                if user.check_password(password):
                    refresh = RefreshToken.for_user(user)
                    return Response(
                        {
                            "tokens": {
                                "refresh": str(refresh),
                                "access": str(refresh.access_token),
                            },
                            "user": {
                                "id": user.id,
                                "username": user.username,
                                "email": user.email,
                            },
                        }
                    )
                else:
                    return Response(
                        {"error": "Invalid credentials"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

            except User.DoesNotExist:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logged out successfully."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except TokenError:
            return Response(
                {"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = UserProfileSerializer
    update_service = UserUpdateService(
        {
            "username": UniqueFieldValidator(
                "username", "This username is already taken."
            ),
            "email": UniqueFieldValidator("email", "This email is already in use."),
            "password": PasswordValidator(),
        }
    )

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        if user.profile_photo:
            user.profile_photo.delete()
            user.profile_photo = None
            user.save()
            return Response(
                {"message": "Profile photo removed."}, status=status.HTTP_200_OK
            )
        return Response(
            {"error": "No profile photo to remove."}, status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request):
        """
        Handle PATCH request for user profile update
        """
        user = request.user
        update_data = request.data

        success, error = self.update_service.update_user(user, update_data)

        if not success:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddCityToUserView(APIView):
    """
    View to add a city to a user's cities
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CitySerializer

    def post(self, request):
        """
        Add a city to a user's cities by username or user ID
        """
        city_id = request.data.get("city_id")
        username = request.data.get("username")
        user_id = request.data.get("user_id")

        try:
            city = City.objects.get(id=city_id)

            if username:
                user_to_add = User.objects.get(username=username)
            elif user_id:
                user_to_add = User.objects.get(id=user_id)
            else:
                return Response(
                    {"detail": "Must provide either username or user_id"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_to_add.cities.add(city)

            return Response(
                {
                    "detail": "City added successfully",
                    "city": self.serializer_class(city).data,
                    "added_to_user": user_to_add.username,
                },
                status=status.HTTP_200_OK,
            )

        except City.DoesNotExist:
            return Response(
                {"detail": "City not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
