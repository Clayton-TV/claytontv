from django.db import models
from django.urls import reverse  # generate urls by reversing url pattern
import csv
from .models/bible_book import Bible_Book

def import_bible(bible_path):
    with open(bible_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            models.bible_book.Bible_Book.objects.create(
                title=row[0],
                author=row[1],
                summary=row[2],
                type=row[3]
            )


if __name__ == '__main__':
    Bible_CSV_Path = 'CSV/Bible Books.csv'
    import_bible(Bible_CSV_Path)
