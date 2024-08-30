import csv
from django.core.management.base import BaseCommand, CommandError
from catalogue.models.bible_book import Bible_Book


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "--DEBUG",
            action="store_true",
            help="Runs the command with Debug on",
        )

    def handle(self, *args, **options):
        Debug = False
        if options["DEBUG"]:
            Debug = True
        self.imp_bible("CSV/Bible Books.csv",Debug) #calls the function that imports the CSV at the file path into the Bible_Book data table.

    def imp_bible(self,filepath,Debug):
        if Debug:
            print("The command ran and:")
        Bible_Book.objects.all().delete()
        with open(filepath, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if Debug:
                    print(row)
                    print("Imported " + row['name'])
                Bible_Book.objects.create(
                    order=row['order'],
                    name=row['code'],
                    summary=row['name'],
                    type=row['type']
                )
