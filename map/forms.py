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

    city = forms.ChoiceField(
        label="Select a City",
        choices=[],
        widget=forms.Select(attrs={"class": "map-city-search-input"}),
    )

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["city"].choices = self.get_city_choices(user)

    def get_city_choices(self, user):
        cache_key = self.CACHE_KEY.format(user_id=user.id)
        choices = cache.get(cache_key)

        if choices is None:
            cities = user.cities.annotate(places_count=Count("places"))
            choices = [
                (city.id, f"{city.name} ({city.places_count} places)")
                for city in cities
            ]
            cache.set(cache_key, choices, self.CACHE_TIMEOUT)

        return choices
