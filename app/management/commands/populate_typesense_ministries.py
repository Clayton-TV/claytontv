import typesense
from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.models.ministry import Ministry


class Command(BaseCommand):
    help = "Populate all Ministries into Typesense"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.populate_ministries(options["DEBUG"])

    def populate_ministries(self, debug):
        client = typesense.Client(settings.TYPESENSE_PARAMS)
        if debug:
            self.stdout.write("Attempting to delete any existing ministry collection")
        try:
            client.collections["ministry"].delete()
        except typesense.exceptions.ObjectNotFound:
            if debug:
                self.stdout.write("No pre-existing collection to delete")
        schema = {
            "name": "ministry",
            "fields": [
                {"name": "name", "type": "string"},
                {"name": "summary", "type": "string"},
                {"name": "django_url", "type": "string"},
            ],
        }
        if debug:
            self.stdout.write("Creating collection for ministry")
        client.collections.create(schema)
        for i in Ministry.objects.all():
            if debug:
                self.stdout.write(f"Creating document for: {i.name}")
            client.collections["ministry"].documents.create(
                {
                    "name": i.name,
                    "summary": i.summary,
                    "django_url": i.get_absolute_url(),
                }
            )
