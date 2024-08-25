import csv
from catalogue.models.bible_book import Bible_Book


def import_bible(bible_path):
    with open(bible_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Bible_Book.objects.create(
                title=row[0],
                author=row[1],
                summary=row[2],
                type=row[4]
            )


if __name__ == '__main__':
    Bible_CSV_Path = 'CSV/Bible Books.csv'
    import_bible(Bible_CSV_Path)
