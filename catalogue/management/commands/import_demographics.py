import csv
import sys
from pathlib import Path

from django.core.management.base import BaseCommand

from catalogue.models.demograpic import Demographic

csv.field_size_limit(sys.maxsize)


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.imp_demographics("CSV/Demographics.csv", options["DEBUG"])

    def imp_demographics(self, filepath, debug):
        if debug:
            self.stdout.write("The command ran and:")  # Debug Text
        Demographic.objects.all().delete()
        with Path(filepath).open(encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:  # cycles through the row of the dictionary previously created.
                if debug:  # Debug Text
                    self.stdout.write(str(row))  # Debug Text
                    self.stdout.write(f"Imported {row['Name']}")  # Debug Text
                Demographic.objects.create(
                    name=row["Name"],
                    summary=row["Summary"],
                    # series=row['Series'], Not added at this point
                    # topic=row['Topics'], Not added at this point
                    # videos=row['Videos'], Not added at this point
                    # channel=row['Channel'], Not added at this point
                    thumbnail=row["Thumbnail"],
                )
