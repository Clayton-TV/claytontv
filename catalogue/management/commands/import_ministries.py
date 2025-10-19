import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from catalogue.models.ministry import Ministry


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.imp_ministries("CSV/Ministry.csv", options["DEBUG"])

    def imp_ministries(self, filepath, debug):
        if debug:
            self.stdout.write("The command ran and:")  # Debug Text
        Ministry.objects.all().delete()
        with Path(filepath).open(encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:  # cycles through the row of the dictionary previously created.
                if debug:  # Debug Text
                    self.stdout.write(str(row))  # Debug Text
                    self.stdout.write(f"Imported {row['Name']}")  # Debug Text
                Ministry.objects.create(
                    name=row["Name"],
                    summary=row["Summary"],
                    # videos=row['Videos'], Not added at this point
                    # series=row['Series'], Not added at this point
                    # channel=row['Channel'], Not added at this point
                    thumbnail=row["Thumbnail"],
                )
