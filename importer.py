import csv
from django.core.management.base import BaseCommand, CommandError
from catalogue.models.bible_book import Bible_Book


class Command(BaseCommand):
    def Importer(self):
        Bible_CSV_Path = 'CSV/Bible Books.csv'
        with open(bible_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Bible_Book.objects.create(
                    title=row[0],
                    author=row[1],
                    summary=row[2],
                    type=row[4]
                )
