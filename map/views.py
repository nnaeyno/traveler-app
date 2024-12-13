from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import LocationForm
from django.views.generic import TemplateView


class MapView(TemplateView):
    template_name = "city.html"


def add_location(request):
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            # Process the form data (e.g., save to the database)
            # For now, just return a success response
            return HttpResponse("Location added successfully!")
    else:
        form = LocationForm()

    return render(request, "city.html", {"form": form})
