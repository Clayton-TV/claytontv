# ruff: noqa: T201,T203,F401,F403,F405,F821,E501,E203,W292,W391,N801,N802,N803,N804,N805,N806,N807,N813,N814,F821,N999,PTH123,C901


import csv

import django.core.exceptions
from django.core.management.base import BaseCommand

from catalogue.models.bible_book import Bible_Book
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
        self.link_videos(
            "CSV/Videos.csv", options["DEBUG"]
        )  # calls the function that imports the CSV at the file path into the Bible_Book data table. It also passes the result of options["DEBUG"] which checks if the debug command has been called.

    def CleanID(self, ItemIn):
        SymbolsToStrip = " '[]-—"
        ItemOut = ItemIn.strip(SymbolsToStrip)
        return ItemOut

    def link_videos(self, filepath, Debug):
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
            skipped_bible_books = []
            for row in reader:  # cycles through the row of the dictionary previously created.
                if Debug:  # Debug Text
                    print(row)  # Debug Text
                    print(
                        "Linked " + row["Name"]
                    )  # Debug Text, note that the rows are referred to by the column headers in the dict

                topics = self.CleanID(row["Topic"]).replace(";", ",").split(",")
                speaker = self.CleanID(row["Speaker/Artist"]).split(";")
                bbook = self.CleanID(row["Bible Book"]).replace(";", ",").split(",")

                try:
                    Vid = Video.objects.get(id=row["ID"])

                except django.core.exceptions.ObjectDoesNotExist:
                    # print("The entry " + row["ID"] + " does not exist")
                    skipped_videos.append(row["ID"])

                except django.core.exceptions.MultipleObjectsReturned:
                    print("The entry " + row["ID"] + " returned duplicate elements")

                else:
                    Vid.topic.clear()
                    Vid.speaker.clear()
                    Vid.bible_book.clear()

                    for i in topics:
                        try:
                            Vid.topic.add(Topic.objects.get(name=i))  # function to match the old topic to the new

                        except django.core.exceptions.ObjectDoesNotExist:
                            print("The Topic " + i + " does not exist")

                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The Topic " + i + " returned duplicate elements")

                    for i in bbook:
                        try:
                            Vid.bible_book.add(
                                Bible_Book.objects.get(summary=i)
                            )  # function to match the old bible book to the new

                        except django.core.exceptions.ObjectDoesNotExist:
                            # print("The Bible Book " + i + " does not exist")
                            if i == "Song of Songs":
                                try:
                                    Vid.bible_book.add(Bible_Book.objects.get(summary="Song of Solomon"))
                                except django.core.exceptions.ObjectDoesNotExist:
                                    skipped_bible_books.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The Bible Book " + i + " returned duplicate elements")

                    for i in speaker:
                        if i == "Cree. Steve":  # catching some annoying typos in the CSV
                            i = "Steve Cree"
                        elif i == "Diwakar. George":
                            i = "George Diwakar"
                        if i == "":
                            continue
                        if len(i.split(",")) > 1:
                            i = (
                                i.split(",")[1].strip() + " " + i.split(",")[0].strip()
                            )  # Switches the name from Last, First to First Last
                        else:
                            i = i.strip().strip('"').strip("'")
                        try:
                            Vid.speaker.add(Speaker.objects.get(name=i))

                        except django.core.exceptions.ObjectDoesNotExist:
                            # print("The Speaker " + i + " does not exist")
                            skipped_speakers.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The Speaker " + i + " returned duplicate elements")
            print("The following video IDs were skipped as they do not exist:")
            print(set(skipped_videos))
            print("Total of " + str(len(set(skipped_videos))) + " skipped videos")
            print("The following speakers were skipped as they do not exist:")
            print(repr(set(skipped_speakers)))
            print("Total of " + str(len(set(skipped_speakers))) + " skipped speakers")
            print("The following bible books were skipped as they do not exist:")
            print(repr(set(skipped_bible_books)))
            print("Total of " + str(len(set(skipped_bible_books))) + " skipped bible books")


class TO2N:  # Topic Old to New
    TopicTable = 0
    filepath = "CSV/topics-mergers.csv"

    def __init__(self):
        with open(
            self.filepath, encoding="utf-8-sig"
        ) as file:  # Opens the file path at "filepath" readonly as the variable "file".
            self.TopicTable = csv.DictReader(
                file
            )  # opens file with using the CSV's library Dictreader which converts it into a dictionary, the headers are the key for each row.
