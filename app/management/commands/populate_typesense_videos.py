import typesense
from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.models.video import Video


class Command(BaseCommand):
    help = "Populate all Videos into Typesense"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.populate_videos(options["DEBUG"])

    def populate_videos(self, debug):
        ts_config = settings.TYPESENSE_PARAMS
        ts_config["connection_timeout_seconds"] = 300
        client = typesense.Client(ts_config)
        if debug:
            self.stdout.write("Attempting to delete any existing video collection")
        try:
            client.collections["video"].delete()
        except typesense.exceptions.ObjectNotFound:
            if debug:
                self.stdout.write("No pre-existing collection to delete")
        schema = {
            "name": "video",
            "fields": [
                {"name": "video_id", "type": "string"},
                {"name": "id_number", "type": "string"},
                {"name": "name", "type": "string"},
                {"name": "description", "type": "string"},
                {"name": "url", "type": "string"},
                {"name": "number_in_series", "type": "int32", "optional": True},
                {"name": "is_livestream", "type": "bool", "facet": True},
                {"name": "date_recorded", "type": "int64"},
                {"name": "date_created", "type": "int64"},
                {"name": "date_modified", "type": "int64"},
            ],
        }
        if debug:
            self.stdout.write("Creating collection for video")
        client.collections.create(schema)
        data_to_upload = []
        for i in Video.objects.all():
            if debug:
                self.stdout.write(f"Creating document for: {i.name}")
            data_to_upload.append(
                {
                    "video_id": i.id,
                    "id_number": i.id_number,
                    "name": i.name,
                    "description": i.description,
                    "url": i.url,
                    "number_in_series": i.number_in_series,
                    "is_livestream": i.is_livestream,
                    "date_recorded": int(i.date_recorded.strftime("%s")),
                    "date_created": int(i.date_created.strftime("%s")),
                    "date_modified": int(i.date_modified.strftime("%s")),
                }
            )

        client.collections["video"].documents.import_(data_to_upload, {"action": "create"})
