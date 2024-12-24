from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import ChecklistItem, Trip

""" to showcase different approaches/techniques when creating views in django, here are function based views """


@login_required
def create_trip(request):
    if request.method == "POST":
        name = request.POST["name"]
        destination = request.POST["destination"]
        start_date = request.POST["start_date"]
        end_date = request.POST["end_date"]
        trip = Trip.objects.create(
            name=name,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            user=request.user,
        )
        return redirect("trip_detail", trip_id=trip.id)
    return render(request, "create_trip.html")  # doesn't exist for now


@login_required
def add_checklist_item(request, trip_id):
    trip = Trip.objects.get(id=trip_id, user=request.user)
    if request.method == "POST":
        name = request.POST["name"]
        ChecklistItem.objects.create(name=name, trip=trip)
        return redirect("trip_detail", trip_id=trip.id)
    return render(
        request, "add_checklist_item.html", {"trip": trip}
    )  # doesn't exist for now