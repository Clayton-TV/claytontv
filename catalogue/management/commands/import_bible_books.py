import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from catalogue.models.bible_book import BibleBook  # Updated to use the new class name


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",  # Stores whether this option has been called or not.
            # If called, it will return true when queried.
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.imp_bible("CSV/Bible Books.csv", options["DEBUG"])  # Imports CSV data into BibleBook model
        # Uses DEBUG option to control logging verbosity

    def imp_bible(self, filepath, debug):
        if debug:
            self.stdout.write("The command ran and:")  # Debug Text using logger instead of print
        BibleBook.objects.all().delete()  # Clears all existing data before reimporting
        # This is useful but potentially dangerous
        with Path(filepath).open(encoding="utf-8-sig") as file:  # Opens the file path using Path
            reader = csv.DictReader(file)  # Opens file using CSV's DictReader, converting to a dictionary.
            # Headers become keys for each row.
            for row in reader:  # cycles through the row of the dictionary previously created.
                if debug:  # Debug Text
                    self.stdout.write(str(row))  # Debug info using logger instead of print
                    self.stdout.write(f"Imported {row['name']}")  # Debug info using logger
                BibleBook.objects.create(  # Create an entry in bible books.
                    order=row["order"],  # added the order to the entry
                    name=row["code"],  # adds the book code to the entry
                    summary=row["name"],  # stores the name of the book to the entry
                    type=row["type"],  # stores type of that bible book to the entry
                )
