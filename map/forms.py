from datetime import datetime

import jwt
import requests
from django import forms
from django.core.cache import cache
from django.db.models import Count


class LocationForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Place Name"}),
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Description"}), required=False
    )
    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())


class CitySearchForm(forms.Form):
    CACHE_KEY = "city_choices_{user_id}"
    CACHE_TIMEOUT = 3600  # 1 hour
    url = 'http://127.0.0.1:8000/api/cities/'

    city = forms.ChoiceField(
        label="Select a City",
        choices=[],
        widget=forms.Select(attrs={"class": "map-city-search-input"}),
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if request:

            self.access_token = (
                    request.session.get('access_token') or
                    request.COOKIES.get('access_token') or
                    getattr(request.user, 'auth_token', None)
            )
            if self.access_token:
                self.fields["city"].choices = self.get_city_choices(request)

    def get_city_choices(self, request):
        if not self.access_token:
            print("No access token found")
            return []

        try:
            decoded = jwt.decode(self.access_token, options={"verify_signature": False})
            print("Decoded Token:", decoded)

            exp_timestamp = decoded.get('exp')
            if exp_timestamp and datetime.fromtimestamp(exp_timestamp) < datetime.now():
                print("Token is expired")
                return []

        except Exception as e:
            print(f"Exception decoding token: {str(e)}")
            return []

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'X-CSRFToken': request.COOKIES.get('csrftoken'),
            }

            cookies = {
                'sessionid': request.COOKIES.get('sessionid'),
                'csrftoken': request.COOKIES.get('csrftoken'),
            }

            print("Headers being sent:", headers)
            response = requests.get(
                self.url,
                headers=headers,
                cookies=cookies,
                verify=True
            )

            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            print(f"Response Body: {response.text}")

            if response.status_code == 200:
                cities_data = response.json()
                return [
                    (city['id'], f"{city['name']} ({city['places_count']} places)")
                    for city in cities_data
                ]
            else:
                print(f"Error: Status code {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected Exception: {str(e)}")
            return []


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'login-form-input',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'login-form-input',
            'placeholder': 'Password'
        })
    )
