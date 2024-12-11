from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db import models

from roadrunner import settings


class Location(models.Model):
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return f"{self.lat}, {self.lng}"


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Place(models.Model):
    """
    Represents a place with detailed information and user interactions
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Place Name"
    )
    description = models.TextField(
        verbose_name="Place Description",
        blank=True
    )
    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        related_name='places'
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.CASCADE,
        related_name='places'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    photo = models.ImageField(
        upload_to="places_photo/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])
        ]
    )

    # Aggregated Rating Fields
    total_ratings = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ]
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def update_rating(self):
        """
        Recalculate average rating based on all place ratings
        """
        ratings = self.ratings.all()
        if ratings:
            self.total_ratings = ratings.count()
            self.average_rating = ratings.aggregate(
                models.Avg('rating')
            )['rating__avg']
            self.save()


class PlaceRating(models.Model):
    """
    Represents a user's rating for a specific place
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='place_ratings'
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'place']
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """
        Override save to update place's average rating
        """
        super().save(*args, **kwargs)
        self.place.update_rating()


class PlaceComment(models.Model):
    """
    Represents a user's comment about a place
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='place_comments'
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class UserPlaceVisit(models.Model):
    """
    Tracks whether a user has visited a place
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='place_visits'
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='visits'
    )
    visited_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField()

    class Meta:
        unique_together = ['user', 'place']
        ordering = ['-visited_at']

    @classmethod
    def mark_as_visited(cls, user, place):
        """
        Convenience method to mark a place as visited
        """
        return cls.objects.get_or_create(user=user, place=place)
