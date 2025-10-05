# ruff: noqa: T201,T203,F401,F403,F405,F821,E501,E203,W292,W391,N801,N802,N803,N804,N805,N806,N807,N813,N814,F821,N999,PTH123,C901

import csv

import django.core.exceptions
from django.core.management.base import BaseCommand

from catalogue.models.ministry import Ministry
from catalogue.models.series import Series
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
        self.link_ministries(
            "CSV/Ministry.csv", options["DEBUG"]
        )  # calls the function that imports the CSV at the file path into the Bible_Book data table. It also passes the result of options["DEBUG"] which checks if the debug command has been called.

    def CleanID(self, ItemIn):
        SymbolsToStrip = " '[]-—"
        ItemOut = ItemIn.strip(SymbolsToStrip)
        return ItemOut

    def link_ministries(self, filepath, Debug):
        if Debug:
            print("The command ran and:")  # Debug Text
        with open(
            filepath, encoding="utf-8-sig"
        ) as file:  # Opens the file path at "filepath" readonly as the variable "file".
            reader = csv.DictReader(
                file
            )  # opens file with using the CSV's' library Dictreader which converts it into a dictionary, the headers are the key for each row.

            skipped_videos = []
            skipped_series = []
            linked_series = 0
            for row in reader:  # cycles through the row of the dictionary previously created.
                if Debug:  # Debug Text
                    print(row)  # Debug Text
                    print(
                        "Linked " + row["Name"]
                    )  # Debug Text, note that the rows are referred to by the column headers in the dict

                videos = self.CleanID(row["Video_ids"]).split(",")
                series = self.CleanID(row["Series"]).split(",")

                try:
                    Min = Ministry.objects.get(name=row["Name"])

                except django.core.exceptions.ObjectDoesNotExist:
                    print("The entry " + row["Name"] + " does not exist")

                except django.core.exceptions.MultipleObjectsReturned:
                    print("The entry " + row["Name"] + " returned duplicate elements")

                else:
                    Min.videos.clear()

                    for i in videos:
                        try:
                            Min.videos.add(Video.objects.get(id=i))

                        except django.core.exceptions.ObjectDoesNotExist:
                            # print("The Video " + i + " does not exist")
                            skipped_videos.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The Video " + i + " returned duplicate elements")
                # Series linking:
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
                        Min.series.add(Series.objects.get(name=i))
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
                                Min.series.add(Series.objects.get(name=LongTermMemory + i))
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
                                Min.series.add(Series.objects.get(name=Memory + i))
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
                                Min.series.add(Series.objects.get(name=LongTermMemory + i))
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
            print("The following video IDs were skipped as they do not exist:")
            print(set(skipped_videos))
            print("Total of " + str(len(set(skipped_videos))) + " skipped videos")
            print("The following series were skipped as they do not exist:")
            print(set(skipped_series))
            print("Total of " + str(len(set(skipped_series))) + " skipped series")
            print("A total of " + str(linked_series) + " series were linked")
