import typesense
from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.models.channel import Channel


class Command(BaseCommand):
    help = "Populate all Channels into Typesense"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.populate_channels(options["DEBUG"])

    def populate_channels(self, debug):
        client = typesense.Client(settings.TYPESENSE_PARAMS)
        if debug:
            self.stdout.write("Attempting to delete any existing channel collection")
        try:
            client.collections["channel"].delete()
        except typesense.exceptions.ObjectNotFound:
            if debug:
                self.stdout.write("No pre-existing collection to delete")
        schema = {
            "name": "channel",
            "fields": [
                {"name": "name", "type": "string"},
                {"name": "summary", "type": "string"},
                {"name": "type", "type": "string", "facet": True},
                {"name": "channel_url", "type": "string"},
                {"name": "trusted", "type": "bool", "facet": True},
                {"name": "django_url", "type": "string"},
                # TO-DO do we need to index the other fields which are ManyToManyField or ForeignKey?
            ],
        }
        if debug:
            self.stdout.write("Creating collection for channel")
        client.collections.create(schema)
        for i in Channel.objects.all():
            if debug:
                self.stdout.write(f"Creating document for: {i.name}")
            client.collections["channel"].documents.create(
                {
                    "name": i.name,
                    "summary": i.summary,
                    "type": i.type,
                    "channel_url": i.channel_url,
                    "trusted": i.trusted,
                    "django_url": i.get_absolute_url(),
                }
            )
