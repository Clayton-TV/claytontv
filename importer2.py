from catalogue.models.bible_book import Bible_Book
from django.test import TestCase
import csv


class BibleBookTest(TestCase):

    def setUp(self):
        file_path = 'CSV/Bible Books.csv'

        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)

            for row in reader:
                Bible_Book.objects.create(
                    order=row['order'],
                    name=row['name'],
                    summary=row['name'],
                    type=row['type'])

    def test_bible_book_order(self):
        book = Bible_Book.objects.get(name='Genesis')
        self.assertEqual(book.order, '1')