# ruff: noqa: C901
import csv
from pathlib import Path

import django.core.exceptions
from django.core.management.base import BaseCommand

from catalogue.models.bible_book import Bible_Book
from catalogue.models.series import Series
from catalogue.models.speaker import Speaker
from catalogue.models.topic import Topic
from catalogue.models.video import Video


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.link_series("CSV/Series.csv", options["DEBUG"])

    def clean_id(self, item_in):
        symbols_to_strip = " '[]-—"
        item_out = item_in.strip(symbols_to_strip)
        return item_out

    def link_series(self, filepath, debug):
        if debug:
            self.stdout.write("The command ran and:")  # Debug Text

        with Path(filepath).open(encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            skipped_videos = []
            skipped_speakers = []
            skipped_topics = []
            skipped_bible_books = []
            for row in reader:  # cycles through the row of the dictionary previously created.
                if debug:  # Debug Text
                    self.stdout.write(str(row))  # Debug Text
                    self.stdout.write(f"Linked {row['Name']}")  # Debug Text

                topics = self.clean_id(row["topic_name"]).replace(";", ",").split(",")
                speaker = self.clean_id(row["speaker_id"]).replace(" ", ",").split(",")
                videos = self.clean_id(row["video_id"]).split(",")
                bbook = self.clean_id(row["bbook_names"]).replace(";", ",").split(",")

                try:
                    ser = Series.objects.get(id_number=row["ID"])

                except django.core.exceptions.ObjectDoesNotExist:
                    self.stdout.write(f"The entry {row['ID']} does not exist")

                except django.core.exceptions.MultipleObjectsReturned:
                    self.stdout.write(f"The entry {row['ID']} returned duplicate elements")

                else:
                    ser.topic.clear()
                    ser.speaker.clear()
                    ser.videos.clear()
                    ser.bible_book.clear()

                    for i in bbook:
                        try:
                            ser.bible_book.add(Bible_Book.objects.get(summary=i))

                        except django.core.exceptions.ObjectDoesNotExist:
                            if i == "Song of Songs":
                                try:
                                    ser.bible_book.add(Bible_Book.objects.get(summary="Song of Solomon"))
                                except django.core.exceptions.ObjectDoesNotExist:
                                    skipped_bible_books.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            self.stdout.write(f"The Bible Book {i} returned duplicate elements")

                    for i in topics:
                        try:
                            ser.topic.add(Topic.objects.get(name=i))

                        except django.core.exceptions.ObjectDoesNotExist:
                            skipped_topics.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            self.stdout.write(f"The Topic {i} returned duplicate elements")

                    for i in speaker:
                        try:
                            ser.speaker.add(Speaker.objects.get(id=i))

                        except django.core.exceptions.ObjectDoesNotExist:
                            skipped_speakers.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            self.stdout.write(f"The Speaker {i} returned duplicate elements")

                    for i in videos:
                        try:
                            ser.videos.add(Video.objects.get(id=i))

                        except django.core.exceptions.ObjectDoesNotExist:
                            skipped_videos.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            self.stdout.write(f"The Video {i} returned duplicate elements")

            self.stdout.write("The following video IDs were skipped as they do not exist:")
            self.stdout.write(str(set(skipped_videos)))
            self.stdout.write(f"Total of {len(set(skipped_videos))} skipped videos")
            self.stdout.write("The following speakers were skipped as they do not exist:")
            self.stdout.write(repr(set(skipped_speakers)))
            self.stdout.write(f"Total of {len(set(skipped_speakers))} skipped")
            self.stdout.write("The following topics were skipped as they do not exist:")
            self.stdout.write(repr(set(skipped_topics)))
            self.stdout.write(f"Total of {len(set(skipped_topics))} skipped topics")
            self.stdout.write("The following bible books were skipped as they do not exist:")
            self.stdout.write(repr(set(skipped_bible_books)))
            self.stdout.write(f"Total of {len(set(skipped_bible_books))} skipped bible books")
