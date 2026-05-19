import typesense
from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.models.topic import Topic


class Command(BaseCommand):
    help = "Populate all Topics into Typesense"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.populate_topics(options["DEBUG"])

    def populate_topics(self, debug):
        client = typesense.Client(settings.TYPESENSE_PARAMS)
        if debug:
            self.stdout.write("Attempting to delete any existing topic collection")
        try:
            client.collections["topic"].delete()
        except typesense.exceptions.ObjectNotFound:
            if debug:
                self.stdout.write("No pre-existing collection to delete")
        schema = {
            "name": "topic",
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "name", "type": "string"},
                {"name": "summary", "type": "string"},
                {"name": "category", "type": "string", "facet": True},
            ],
        }
        if debug:
            self.stdout.write("Creating collection for topic")
        client.collections.create(schema)
        for i in Topic.objects.all():
            if debug:
                self.stdout.write(f"Creating document for: {i.name}")
            client.collections["topic"].documents.create(
                {
                    "id": i.id,
                    "name": i.name,
                    "summary": i.summary,
                    "category": i.category,
                }
            )
