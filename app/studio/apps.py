from django.apps import AppConfig


class StudioConfig(AppConfig):
    # Distinct label so it doesn't collide with the parent "app" app; lets
    # Django discover the create_editor management command.
    name = "app.studio"
    label = "studio"
