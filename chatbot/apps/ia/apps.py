from django.apps import AppConfig


class IAConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ia'

    def ready(self):
        import ia.signals  # noqa
        import ia.lookups  # noqa
