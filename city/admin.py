from django.contrib import admin
from django.utils.html import format_html
from .models import Location, City, Place, PlaceRating, PlaceComment, UserPlaceVisit


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'lat', 'lng', 'get_places')
    search_fields = ('lat', 'lng')

    def get_places(self, obj):
        return ", ".join([place.name for place in obj.places.all()])

    get_places.short_description = 'Associated Places'


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_places_count')
    search_fields = ('name',)

    def get_places_count(self, obj):
        return obj.places.count()

    get_places_count.short_description = 'Number of Places'


class PlaceRatingInline(admin.TabularInline):
    model = PlaceRating
    extra = 0
    readonly_fields = ('created_at',)
    raw_id_fields = ('user',)


class PlaceCommentInline(admin.TabularInline):
    model = PlaceComment
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)


class UserPlaceVisitInline(admin.TabularInline):
    model = UserPlaceVisit
    extra = 0
    readonly_fields = ('visited_at',)
    raw_id_fields = ('user',)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'price', 'average_rating', 'total_ratings',
                    'display_photo', 'created_at')
    list_filter = ('city', 'created_at')
    search_fields = ('name', 'description', 'city__name')
    readonly_fields = ('created_at', 'updated_at', 'total_ratings', 'average_rating',
                       'display_photo_large')
    raw_id_fields = ('location',)
    inlines = [PlaceRatingInline, PlaceCommentInline, UserPlaceVisitInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'city', 'price')
        }),
        ('Location', {
            'fields': ('location',)
        }),
        ('Media', {
            'fields': ('photo', 'display_photo_large')
        }),
        ('Statistics', {
            'fields': ('total_ratings', 'average_rating')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" height="50"/>', obj.photo.url)
        return "No photo"

    display_photo.short_description = 'Photo'

    def display_photo_large(self, obj):
        if obj.photo:
            return format_html('<img src="{}" height="200"/>', obj.photo.url)
        return "No photo"

    display_photo_large.short_description = 'Photo Preview'


@admin.register(PlaceRating)
class PlaceRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'place', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'place__name')
    raw_id_fields = ('user', 'place')
    readonly_fields = ('created_at',)


@admin.register(PlaceComment)
class PlaceCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'place', 'text_preview', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'place__name', 'text')
    raw_id_fields = ('user', 'place')
    readonly_fields = ('created_at', 'updated_at')

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    text_preview.short_description = 'Comment Preview'


@admin.register(UserPlaceVisit)
class UserPlaceVisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'place', 'visited_at', 'notes_preview')
    list_filter = ('visited_at',)
    search_fields = ('user__username', 'place__name', 'notes')
    raw_id_fields = ('user', 'place')
    readonly_fields = ('visited_at',)

    def notes_preview(self, obj):
        return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes

    notes_preview.short_description = 'Notes Preview'
