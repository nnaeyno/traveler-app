from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from city.models import City, Place
from map.forms import CitySearchForm


@receiver([post_save, post_delete], sender=City)
@receiver([post_save, post_delete], sender=Place)
def invalidate_city_choices_cache(sender, instance, **kwargs):
    if isinstance(instance, Place):
        user_id = instance.city.user_id
    else:  # City
        user_id = instance.user_id

    cache_key = CitySearchForm.CACHE_KEY.format(user_id=user_id)
    cache.delete(cache_key)
