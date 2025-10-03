# ruff: noqa: T201,T203,F401,F403,F405,F821,E501,E203,W292,W391,N801,N802,N803,N804,N805,N806,N807,N813,N814,F821,N999,PTH123,C901

import csv
import sys

import django.core.exceptions
from django.core.management.base import BaseCommand

from catalogue.models.demograpic import Demographic
from catalogue.models.series import Series
from catalogue.models.topic import Topic
from catalogue.models.video import Video

csv.field_size_limit(sys.maxsize)


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",  # In this case it stores that the whether this option has been called or not, if it has it will return true when queried.
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.link_demographics(
            "CSV/Demographics.csv", options["DEBUG"]
        )  # calls the function that imports the CSV at the file path into the Bible_Book data table. It also passes the result of options["DEBUG"] which checks if the debug command has been called.

    def CleanID(self, ItemIn):
        # Recursive cleaner
        if isinstance(ItemIn, list | tuple):
            # Clean each sub-item and join with commas
            return ",".join(self.CleanID(i) for i in ItemIn)
        elif isinstance(ItemIn, str):
            # Strip only unwanted edge characters
            return ItemIn.strip(" '\"[]()")
        else:
            return str(ItemIn)

    def link_demographics(self, filepath, Debug):
        if Debug:
            print("The command ran and:")  # Debug Text

        with open(
            filepath, encoding="utf-8-sig"
        ) as file:  # Opens the file path at "filepath" readonly as the variable "file".
            reader = csv.DictReader(
                file
            )  # opens file with using the CSV's' library Dictreader which converts it into a dictionary, the headers are the key for each row.
            skipped_videos = []
            linked_videos = 0
            skipped_series = []
            linked_series = 0
            skipped_topics = []
            linked_topics = 0
            for row in reader:  # cycles through the row of the dictionary previously created.
                if Debug:  # Debug Text
                    print(row)  # Debug Text
                    print(
                        "Linked " + row["Name"]
                    )  # Debug Text, note that the rows are referred to by the column headers in the dict

                topics = self.CleanID(row["Topics"]).replace(";", ",").split(",")
                series = self.CleanID(row["Series"]).split(";")
                videos = self.CleanID(row["Videos"]).split(",")

                try:
                    Dem = Demographic.objects.get(name=row["Name"])

                except django.core.exceptions.ObjectDoesNotExist:
                    print("The entry " + row["Name"] + " does not exist")
                    input("Press Enter to continue...")

                except django.core.exceptions.MultipleObjectsReturned:
                    print("The entry " + row["Name"] + " returned duplicate elements")

                else:
                    Dem.topics.clear()
                    Dem.series.clear()
                    Dem.videos.clear()

                    if Debug:
                        print("Linking Topics")
                        # input("Press Enter to continue...")

                    for i in topics:
                        try:
                            Dem.topics.add(Topic.objects.get(name=i))
                            linked_topics += 1

                        except django.core.exceptions.ObjectDoesNotExist:
                            # print("The topic " + i + " does not exist")
                            skipped_topics.append(i)
                            # if Debug:
                            # input("Press Enter to continue...")

                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The topic " + i + " returned duplicate elements")

                        else:
                            if Debug:
                                print("Entry " + i + " linked")

                    if Debug:
                        print("Linking Series")
                        # input("Press Enter to continue...")
                    Memory = ""
                    LongTermMemory = ""
                    LongTermMemoryList = []
                    for i in series:
                        for j in LongTermMemoryList:
                            if j == i:
                                Memory = ""
                                LongTermMemory = ""
                                LongTermMemoryList = []
                                # print("Removed " + j + " from " + i + " to give " + i)

                        try:
                            Dem.series.add(Series.objects.get(name=i))
                            linked_series += 1
                            Memory = ""
                            LongTermMemory = ""
                            LongTermMemoryList = []
                            # input("Press Enter to continue...")

                        except django.core.exceptions.ObjectDoesNotExist:
                            # print("The Series " + i + " does not exist")
                            # skipped_series.append(i)

                            if LongTermMemory != "":
                                try:
                                    Dem.series.add(Series.objects.get(name=LongTermMemory + i))
                                    # print("LT: Linked " + LongTermMemory+i)
                                    linked_series += 1
                                    Memory = ""
                                    LongTermMemory = ""
                                    LongTermMemoryList = []
                                except django.core.exceptions.ObjectDoesNotExist:
                                    # print("LT:The Series " + repr(LongTermMemory+i) + " does not exist")
                                    # skipped_series.append(LongTermMemory)
                                    LongTermMemory = LongTermMemory + i + ","
                                    LongTermMemoryList.append(i)
                                    Memory = i + ","

                            elif Memory != "":
                                try:
                                    Dem.series.add(Series.objects.get(name=Memory + i))
                                    linked_series += 1
                                    Memory = ""
                                    LongTermMemory = ""
                                    LongTermMemoryList = []
                                except django.core.exceptions.ObjectDoesNotExist:
                                    # print("ST: The Series " + Memory+i + " does not exist")
                                    skipped_series.append(Memory)
                                    LongTermMemory = Memory + i + ","
                                    LongTermMemoryList.append(i)
                                    Memory = i + ","
                            else:
                                Memory = i + ","
                                LongTermMemory = ""
                            # input("Press Enter to continue... Memory is now: " + Memory)

                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The Series " + i + " returned duplicate elements")
                            if LongTermMemory != "":
                                try:
                                    Dem.series.add(Series.objects.get(name=LongTermMemory + i))
                                    # print("LT: Linked " + LongTermMemory+i)
                                    linked_series += 1
                                    Memory = ""
                                    LongTermMemory = ""
                                    LongTermMemoryList = []
                                except django.core.exceptions.ObjectDoesNotExist:
                                    print("LT:The Series " + repr(LongTermMemory + i) + " does not exist")
                                    skipped_series.append(LongTermMemory)
                                    LongTermMemory = LongTermMemory + i + ","
                                    LongTermMemoryList.append(i)
                                    Memory = i + ","

                        else:
                            if Debug:
                                print("Entry " + i + " linked")

                    if Debug:
                        print("Linking Videos")
                        # input("Press Enter to continue...")
                    for i in videos:
                        try:
                            Dem.videos.add(Video.objects.get(id=i))
                            linked_videos += 1

                        except django.core.exceptions.ObjectDoesNotExist:
                            # print("The Video " + i + " does not exist")
                            skipped_videos.append(i)
                            # if Debug:
                            # print(Topic.objects.get(name = 'The Law').id)
                            # input("Press Enter to continue...")

                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The Video " + i + " returned duplicate elements")

                        else:
                            if Debug:
                                print("Entry " + i + " linked")
            # print("The following video IDs were skipped as they do not exist:")
            # print(set(skipped_videos))
            # print("The following series names were skipped as they do not exist:")
            # print(set(skipped_series))
            print("Successfully linked " + str(linked_series) + " series")
            print("Successfully linked " + str(linked_videos) + " videos")
            print("Successfully linked " + str(linked_topics) + " topics")
            print("Skipped " + str(len(skipped_videos)) + " videos")
            print("Skipped " + str(len(skipped_series)) + " series")
            print("Skipped " + str(len(skipped_topics)) + " topics")
