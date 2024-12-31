import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from .Mixin import JWTLoginRequiredMixin
from .forms import CitySearchForm, LocationForm


class PlaceView(TemplateView):
    template_name = "place.html"

    def post(self, request):
        data = {
            "name": request.POST.get("name"),
            "city": request.POST.get("city"),
            "price": request.POST.get("price"),
            "description": request.POST.get("description"),
            "latitude": request.POST.get("latitude"),
            "longitude": request.POST.get("longitude"),
            "user": request.user.id,
        }
        files = {"photo": request.FILES.get("photo")}
        api_url = "http://127.0.0.1:8000/api/places/"
        try:
            response = requests.post(api_url, data=data, files=files)
            if response.status_code == 201:

                return render(
                    request,
                    self.template_name,
                    {"success": "Place added successfully!"},
                )
            else:
                print(response.json())
                return render(request, self.template_name, {"error": response.json()})
        except Exception as e:
            print(str(e))
            return render(request, self.template_name, {"error": str(e)})


class MapView(JWTLoginRequiredMixin, TemplateView):
    template_name = "city.html"
    place_template = "place.html"
    city_search_form = CitySearchForm
    login_url = 'traveler:login'

    def get(self, request, *args, **kwargs):
        form = self.city_search_form(request)
        return self.render_to_response({"form": form})


# testing view
def add_location(request):
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            return HttpResponse("Location added successfully!")
    else:
        form = LocationForm()

    return render(request, "city.html", {"form": form})
