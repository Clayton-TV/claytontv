import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from catalogue.models.speaker import Speaker


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.imp_speakers("CSV/Speakers.csv", options["DEBUG"])

    def imp_speakers(self, filepath, debug):
        if debug:
            self.stdout.write("The command ran and:")  # Debug Text
        Speaker.objects.all().delete()
        with Path(filepath).open(encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:  # cycles through the row of the dictionary previously created.
                if debug:  # Debug Text
                    self.stdout.write(str(row))  # Debug Text
                    self.stdout.write(f"Imported {row['speakerFirstname']} {row['speakerSurname']}")
                if row["speakerFirstname"] is None or row["speakerFirstname"].strip() == "":
                    Speaker.objects.create(
                        id=row["speakerID"],
                        name=row["speakerSurname"].strip(),
                        # bio=row["Bio"],
                        # thumbnail = row["Thumbnail"]
                    )
                else:
                    Speaker.objects.create(
                        id=row["speakerID"],
                        name=row["speakerFirstname"].strip() + " " + row["speakerSurname"].strip(),
                        # bio=row["Bio"],
                        # thumbnail = row["Thumbnail"]
                    )
