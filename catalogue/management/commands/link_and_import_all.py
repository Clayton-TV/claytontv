from django.core.management.base import BaseCommand

from catalogue import search_signals
from catalogue.management.commands.import_all import Command as Import
from catalogue.management.commands.link_all import Command as Link
from catalogue.search import TYPESENSE_ERRORS, SearchUnavailableError, reindex


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        with search_signals.suspended():
            self.stdout.write("Starting Import")
            Import().myimport(options["DEBUG"])
            self.stdout.write("Starting Linking")
            Link().mylink(options["DEBUG"])

        try:
            total = reindex(log=self.stdout.write)
        except (SearchUnavailableError, *TYPESENSE_ERRORS):
            self.stdout.write("Typesense unavailable; skipped search reindex.")
        else:
            self.stdout.write(self.style.SUCCESS(f"Indexed {total} Typesense documents."))

    def clean_id(self, item_in):
        # Recursive cleaner
        if isinstance(item_in, list | tuple):
            # Clean each sub-item and join with commas
            return ",".join(self.clean_id(i) for i in item_in)
        elif isinstance(item_in, str):
            # Strip only unwanted edge characters
            return item_in.strip(" '\"[]()")
        else:
            return str(item_in)
