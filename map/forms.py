# forms.py
from django import forms


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
    city = forms.ChoiceField(
        label="Select a City",
        choices=[],
        widget=forms.Select(attrs={"class": "map-city-search-input"}),
    )
