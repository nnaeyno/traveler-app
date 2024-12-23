from django.contrib import admin

from .models import ChecklistItem, TravelDocument, Trip


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "destination",
        "start_date",
        "end_date",
        "created_at",
    )
    search_fields = ("name", "destination")
    list_filter = ("start_date", "end_date")


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ("name", "trip", "is_packed")
    search_fields = ("name",)
    list_filter = ("is_packed",)


@admin.register(TravelDocument)
class TravelDocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "trip", "user", "uploaded_at")
    search_fields = ("name",)
