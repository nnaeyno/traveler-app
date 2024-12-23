from django.apps import AppConfig


class CityFrontendConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "map"


class YourAppConfig(AppConfig):
    name = 'your_app'

    def ready(self):
        import map.signals