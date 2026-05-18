import typesense
from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.models.bible_book import BibleBook


class Command(BaseCommand):
    help = "Populate all Bible books into Typesense"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.populate_bible_books(options["DEBUG"])

    def populate_bible_books(self, debug):
        client = typesense.Client(settings.TYPESENSE_PARAMS)
        if debug:
            self.stdout.write("Attempting to delete any existing bible_book collection")
        try:
            client.collections["bible_book"].delete()
        except typesense.exceptions.ObjectNotFound:
            if debug:
                self.stdout.write("No pre-existing collection to delete")
        schema = {
            "name": "bible_book",
            "fields": [
                {"name": "order", "type": "string"},
                {"name": "name", "type": "string"},
                {"name": "summary", "type": "string"},
                {"name": "type", "type": "string"},
            ],
        }
        if debug:
            self.stdout.write("Creating collection for bible_book")
        client.collections.create(schema)
        for book in BibleBook.objects.all():
            if debug:
                self.stdout.write(f"Creating document for: {book.name}")
            client.collections["bible_book"].documents.create(
                {"order": book.order, "name": book.name, "summary": book.summary, "type": book.type}
            )
