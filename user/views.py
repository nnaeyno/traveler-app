from django.contrib.auth.password_validation import validate_password
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from .models import User
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Registration successful',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            identifier = serializer.validated_data['identifier']
            password = serializer.validated_data['password']

            try:
                if '@' in identifier:
                    user = User.objects.get(email=identifier)
                else:
                    user = User.objects.get(username=identifier)

                # Check password
                if user.check_password(password):
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'tokens': {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                        },
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email
                        }
                    })
                else:
                    return Response({'error': 'Invalid credentials'},
                                    status=status.HTTP_401_UNAUTHORIZED)

            except User.DoesNotExist:
                return Response({'error': 'Invalid credentials'},
                                status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({'message': 'Logged out successfully.'}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({'error': 'Invalid refresh token.'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
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
            return Response({"message": "Profile photo removed."}, status=status.HTTP_200_OK)
        return Response({"error": "No profile photo to remove."}, status=status.HTTP_400_BAD_REQUEST)


class UserSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        data = request.data
        if 'username' in data:
            new_username = data['username']
            if User.objects.exclude(pk=user.pk).filter(username=new_username).exists():
                return Response(
                    {'username': 'This username is already taken.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.username = new_username

        if 'email' in data:
            new_email = data['email']
            if User.objects.exclude(pk=user.pk).filter(email=new_email).exists():
                return Response(
                    {'email': 'This email is already in use.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = new_email

        if 'profile_photo' in data:
            user.profile_photo = data['profile_photo']

        if 'password' in data:
            new_password = data['password']

            try:
                validate_password(new_password, user)
            except ValidationError as e:
                return Response(
                    {'password': list(e.messages)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(new_password)
        try:
            user.full_clean()
            user.save()
        except ValidationError as e:
            return Response(
                {'detail': e.message_dict},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
