import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from catalogue.models.topic import Topic


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.imp_topics("CSV/Topics.csv", options["DEBUG"])

    def imp_topics(self, filepath, debug):
        if debug:
            self.stdout.write("The command ran and:")  # Debug Text
        Topic.objects.all().delete()
        last_name = ""
        # id_num = 0
        with Path(filepath).open(encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:  # cycles through the row of the dictionary previously created.
                if row["name"] != last_name:
                    if debug:  # Debug Text
                        self.stdout.write(str(row))  # Debug Text
                        self.stdout.write(f"Imported {row['name']}")  # Debug Text
                    Topic.objects.create(
                        id=row["id"],
                        name=row["name"],
                        summary=row["summary"],
                        category=row["category"],
                        # videos=row['Videos'], Not added at this point
                        # series=row['Series'], Not added at this point
                    )
                    # id_num = id_num +1
                    last_name = row["name"]

                else:
                    if debug:  # Debug Text
                        self.stdout.write(str(row))  # Debug Text
                        self.stdout.write(f"skipped {row['name']} as duplicate")
