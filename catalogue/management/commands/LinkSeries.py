# ruff: noqa: T201,T203,F401,F403,F405,F821,E501,E203,W292,W391,N801,N802,N803,N804,N805,N806,N807,N813,N814,F821,N999,PTH123,C901

import csv

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
            action="store_true",  # In this case it stores that the whether this option has been called or not, if it has it will return true when queried.
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.link_series(
            "CSV/Series.csv", options["DEBUG"]
        )  # calls the function that imports the CSV at the file path into the Bible_Book data table. It also passes the result of options["DEBUG"] which checks if the debug command has been called.

    def CleanID(self, ItemIn):
        SymbolsToStrip = " '[]-—"
        ItemOut = ItemIn.strip(SymbolsToStrip)
        return ItemOut

    def link_series(self, filepath, Debug):
        if Debug:
            print("The command ran and:")  # Debug Text

        with open(
            filepath, encoding="utf-8-sig"
        ) as file:  # Opens the file path at "filepath" readonly as the variable "file".
            reader = csv.DictReader(
                file
            )  # opens file with using the CSV's' library Dictreader which converts it into a dictionary, the headers are the key for each row.
            skipped_videos = []
            skipped_speakers = []
            skipped_topics = []
            skipped_bible_books = []
            for row in reader:  # cycles through the row of the dictionary previously created.
                if Debug:  # Debug Text
                    print(row)  # Debug Text
                    print(
                        "Linked " + row["Name"]
                    )  # Debug Text, note that the rows are referred to by the column headers in the dict

                topics = self.CleanID(row["topic_name"]).replace(";", ",").split(",")
                speaker = self.CleanID(row["speaker_id"]).replace(" ", ",").split(",")
                videos = self.CleanID(row["video_id"]).split(",")
                bbook = self.CleanID(row["bbook_names"]).replace(";", ",").split(",")

                try:
                    Ser = Series.objects.get(id_number=row["ID"])

                except django.core.exceptions.ObjectDoesNotExist:
                    print("The entry " + row["ID"] + " does not exist")

                except django.core.exceptions.MultipleObjectsReturned:
                    print("The entry " + row["ID"] + " returned duplicate elements")

                else:
                    Ser.topic.clear()
                    Ser.speaker.clear()
                    Ser.videos.clear()
                    Ser.bible_book.clear()

                    for i in bbook:
                        try:
                            Ser.bible_book.add(
                                Bible_Book.objects.get(summary=i)
                            )  # function to match the old bible book to the new

                        except django.core.exceptions.ObjectDoesNotExist:
                            # print("The Bible Book " + i + " does not exist")
                            if i == "Song of Songs":
                                try:
                                    Ser.bible_book.add(Bible_Book.objects.get(summary="Song of Solomon"))
                                except django.core.exceptions.ObjectDoesNotExist:
                                    skipped_bible_books.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The Bible Book " + i + " returned duplicate elements")

                    for i in topics:
                        try:
                            Ser.topic.add(Topic.objects.get(name=i))

                        except django.core.exceptions.ObjectDoesNotExist:
                            # print("The Topic " + i + " does not exist")
                            skipped_topics.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The Topic " + i + " returned duplicate elements")

                    for i in speaker:
                        try:
                            Ser.speaker.add(Speaker.objects.get(id=i))

                        except django.core.exceptions.ObjectDoesNotExist:
                            # print("The Speaker " + i + " does not exist")
                            skipped_speakers.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The Speaker " + i + " returned duplicate elements")

                    for i in videos:
                        try:
                            Ser.videos.add(Video.objects.get(id=i))

                        except django.core.exceptions.ObjectDoesNotExist:
                            # print("The Video " + i + " does not exist")
                            skipped_videos.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The Video " + i + " returned duplicate elements")

            print("The following video IDs were skipped as they do not exist:")
            print(set(skipped_videos))
            print("Total of " + str(len(set(skipped_videos))) + " skipped videos")
            print("The following speakers were skipped as they do not exist:")
            print(repr(set(skipped_speakers)))
            print("Total of " + str(len(set(skipped_speakers))) + " skipped")
            print("The following topics were skipped as they do not exist:")
            print(repr(set(skipped_topics)))
            print("Total of " + str(len(set(skipped_topics))) + " skipped topics")
            print("The following bible books were skipped as they do not exist:")
            print(repr(set(skipped_bible_books)))
            print("Total of " + str(len(set(skipped_bible_books))) + " skipped bible books")
