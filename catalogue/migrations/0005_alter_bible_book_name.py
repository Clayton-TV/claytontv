# Generated by Django 5.1 on 2024-08-25 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0004_alter_bible_book_name_alter_bible_book_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bible_book",
            name="name",
            field=models.CharField(
                choices=[
                    ("GEN", "Genesis"),
                    ("EXO", "Exodus"),
                    ("LEV", "Leviticus"),
                    ("NUM", "Numbers"),
                    ("DEU", "Deuteronomy"),
                    ("JOS", "Joshua"),
                    ("JUD", "Judges"),
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
                ],
                help_text="Three letter code related to each bible book.",
                max_length=4,
                unique=True,
            ),
        ),
    ]
