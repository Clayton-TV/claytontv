import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from catalogue.models.series import Series


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.imp_series("CSV/Series.csv", options["DEBUG"])

    def imp_series(self, filepath, debug):
        if debug:
            self.stdout.write("The command ran and:")  # Debug Text
        Series.objects.all().delete()
        with Path(filepath).open(encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:  # cycles through the row of the dictionary previously created.
                if debug:  # Debug Text
                    self.stdout.write(str(row))  # Debug Text
                    self.stdout.write(f"Imported {row['series']}")  # Debug Text
                Series.objects.create(
                    name=row["series"],
                    id_number=row["ID"],
                    # summary = row['Summary'],
                    # topic = row['topic'],
                    # speaker = row[speaker],
                    # ministry = row['ministry'],
                    # videos = row[videos],
                    # bible_book = row[bible_bool],
                    year_start=row["dates"][2:5],  # Year-Month-Date
                    year_end=row["dates"][-12:-9],
                )
