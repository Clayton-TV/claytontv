from django.db import models
from django.urls import reverse  # generate urls by reversing url pattern
from django.db import models
from django.urls import reverse  # generate urls by reversing url pattern

BIBLE_BOOKS = (
    ("GEN", "Genesis"),
    ("EXO", "Exodus"),
    ("LEV", "Leviticus"),
    ("NUM", "Numbers"),
    ("DEU", "Deuteronomy"),
    ("JOS", "Joshua"),
    ("JUG", "Judges"),
    ("RUT", "Ruth"),
    ("1SA", "1 Samuel"),
    ("2SA", "2 Samuel"),
    ("1KI", "1 Kings"),
    ("2KI", "2 Kings"),
    ("1CH", "1 Chronicles"),
    ("2CH", "2 Chronicles"),
    ("EZR", "Ezra"),
    ("NEH", "Nehemiah"),
    ("EST", "Esther"),
    ("JOB", "Job"),
    ("PSA", "Psalms"),
    ("PRO", "Proverbs"),
    ("ECC", "Ecclesiastes"),
    ("SOG", "Song of Solomon"),
    ("ISA", "Isaiah"),
    ("JER", "Jeremiah"),
    ("LAM", "Lamentations"),
    ("EZE", "Ezekiel"),
    ("DAN", "Daniel"),
    ("HOS", "Hosea"),
    ("JOE", "Joel"),
    ("AMO", "Amos"),
    ("OBA", "Obadiah"),
    ("JON", "Jonah"),
    ("MIC", "Micah"),
    ("NAH", "Nahum"),
    ("HAB", "Habakkuk"),
    ("ZEP", "Zephaniah"),
    ("HAG", "Haggai"),
    ("ZEC", "Zechariah"),
    ("MAL", "Malachi"),
    ("MAT", "Matthew"),
    ("MAR", "Mark"),
    ("LUK", "Luke"),
    ("JOH", "John"),
    ("ACT", "Acts"),
    ("ROM", "Romans"),
    ("1CO", "1 Corinthians"),
    ("2CO", "2 Corinthians"),
    ("GAL", "Galatians"),
    ("EPH", "Ephesians"),
    ("PHI", "Philippians"),
    ("COL", "Colossians"),
    ("1TH", "1 Thessalonians"),
    ("2TH", "2 Thessalonians"),
    ("1TI", "1 Timothy"),
    ("2TI", "2 Timothy"),
    ("TIT", "Titus"),
    ("PHM", "Philemon"),
    ("HEB", "Hebrews"),
    ("JAS", "James"),
    ("1PE", "1 Peter"),
    ("2PE", "2 Peter"),
    ("1JO", "1 John"),
    ("2JO", "2 John"),
    ("3JO", "3 John"),
    ("JUD", "Jude"),
    ("REV", "Revelation"),
)

BIBLE_BOOK_TYPES = (
    ("LAW", "Law"),
    ("HIS", "History"),
    ("POE", "Poetry"),
    ("PRO", "Prophecy"),
    ("GOS", "Gospel"),
    ("EPI", "Epistle"),
    ("APO", "Apocalyptic"),
)


class Bible_Book(models.Model):
    """Model representing a channel that uploads videos"""

    order = models.CharField(
        max_length=3, help_text="Integer used to sort books into order."
    )
    name = models.CharField(
        max_length=4,
        choices=BIBLE_BOOKS,
        unique=True,
        help_text="Three letter code related to each bible book.",
    )
    summary = models.TextField(
        max_length=5000,
        null=True,
        blank=True,
        help_text="Summary of book of the bible.",
    )
    type = models.CharField(
        max_length=3,
        choices=BIBLE_BOOK_TYPES,
        help_text="Three letter code related to the type of book, e.g. Law, History, Poetry etc.",
    )

    def __str__(self):
        """String for representing channel object"""
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the channel"""
        return reverse("channel-detail", args=[str(self.id)])

    class Meta:
        ordering = ["order"]
