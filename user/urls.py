from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserLoginView, UserLogoutView, UserProfileView, UserRegistrationView, AddCityToUserView

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path('cities/add/', AddCityToUserView.as_view(), name='add-city-to-user'),
]
