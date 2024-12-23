from django.db import models

from city.models import City
from user.models import User


class Trip(models.Model):
    """
    Represents a trip for which the user creates a packing checklist and uploads documents.
    """

    name = models.CharField(max_length=100, verbose_name="Trip Name")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trips")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    destination = models.ForeignKey(
        City, on_delete=models.CASCADE, verbose_name="Destination"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.destination}"


class ChecklistItem(models.Model):
    """
    Represents an item in the packing checklist.
    """

    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name="checklist_items"
    )
    name = models.CharField(max_length=100, verbose_name="Item Name")
    is_packed = models.BooleanField(default=False, verbose_name="Packed Status")

    def __str__(self):
        return self.name


class TravelDocument(models.Model):
    """
    Represents a travel document uploaded by the user for a specific trip.
    """

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="documents")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    name = models.CharField(max_length=100, verbose_name="Document Name")
    file = models.FileField(upload_to="travel_documents/", verbose_name="Document File")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.trip.name}"
