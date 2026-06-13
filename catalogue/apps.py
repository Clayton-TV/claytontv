from django.apps import AppConfig


class CatalogueConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalogue"

    def ready(self):
        # Keep the Typesense index live as catalogue models change.
        from catalogue import search_signals

        search_signals.connect()
