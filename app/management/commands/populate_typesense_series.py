import typesense
from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.models.series import Series


class Command(BaseCommand):
    help = "Populate all Series into Typesense"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.populate_series(options["DEBUG"])

    def populate_series(self, debug):
        ts_config = settings.TYPESENSE_PARAMS
        ts_config["connection_timeout_seconds"] = 300
        client = typesense.Client(ts_config)
        if debug:
            self.stdout.write("Attempting to delete any existing series collection")
        try:
            client.collections["series"].delete()
        except typesense.exceptions.ObjectNotFound:
            if debug:
                self.stdout.write("No pre-existing collection to delete")
        schema = {
            "name": "series",
            "fields": [
                {"name": "name", "type": "string"},
                {"name": "id_number", "type": "string"},
                {"name": "summary", "type": "string", "optional": True},
            ],
        }
        if debug:
            self.stdout.write("Creating collection for series")
        client.collections.create(schema)
        data_to_upload = []
        for i in Series.objects.all():
            if debug:
                self.stdout.write(f"Creating document for: {i.name}")
            data_to_upload.append(
                {
                    "name": i.name,
                    "id_number": i.id_number,
                    "summary": i.summary,
                }
            )

        client.collections["series"].documents.import_(data_to_upload, {"action": "create"})
