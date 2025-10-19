# ruff: noqa: C901
import csv
from pathlib import Path

import django.core.exceptions
from django.core.management.base import BaseCommand

from catalogue.models.demograpic import Demographic
from catalogue.models.series import Series
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
        self.link_demographics("CSV/Demographics.csv", options["DEBUG"])

    def clean_id(self, item_in):
        # Recursive cleaner
        if isinstance(item_in, list | tuple):
            # Clean each sub-item and join with commas
            return ",".join(self.clean_id(i) for i in item_in)
        elif isinstance(item_in, str):
            # Strip only unwanted edge characters
            return item_in.strip(" '\"[]()")
        else:
            return str(item_in)

    def link_demographics(self, filepath, debug):
        if debug:
            self.stdout.write("The command ran and:")  # Debug Text

        with Path(filepath).open(encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            skipped_videos = []
            linked_videos = 0
            skipped_series = []
            linked_series = 0
            skipped_topics = []
            linked_topics = 0
            for row in reader:  # cycles through the row of the dictionary previously created.
                if debug:  # Debug Text
                    self.stdout.write(str(row))  # Debug Text
                    self.stdout.write(f"Linked {row['Name']}")  # Debug Text

                topics = self.clean_id(row["Topics"]).replace(";", ",").split(",")
                series = self.clean_id(row["Series"]).split(";")
                videos = self.clean_id(row["Videos"]).split(",")

                try:
                    dem = Demographic.objects.get(name=row["Name"])

                except django.core.exceptions.ObjectDoesNotExist:
                    self.stdout.write(f"The entry {row['Name']} does not exist")
                    input("Press Enter to continue...")

                except django.core.exceptions.MultipleObjectsReturned:
                    self.stdout.write(f"The entry {row['Name']} returned duplicate elements")

                else:
                    dem.topics.clear()
                    dem.series.clear()
                    dem.videos.clear()

                    if debug:
                        self.stdout.write("Linking Topics")

                    for i in topics:
                        try:
                            dem.topics.add(Topic.objects.get(name=i))
                            linked_topics += 1

                        except django.core.exceptions.ObjectDoesNotExist:
                            skipped_topics.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            self.stdout.write(f"The topic {i} returned duplicate elements")

                        else:
                            if debug:
                                self.stdout.write(f"Entry {i} linked")

                    if debug:
                        self.stdout.write("Linking Series")
                    memory = ""
                    long_term_memory = ""
                    long_term_memory_list = []
                    for i in series:
                        for j in long_term_memory_list:
                            if j == i:
                                memory = ""
                                long_term_memory = ""
                                long_term_memory_list = []

                        try:
                            dem.series.add(Series.objects.get(name=i))
                            linked_series += 1
                            memory = ""
                            long_term_memory = ""
                            long_term_memory_list = []

                        except django.core.exceptions.ObjectDoesNotExist:
                            if long_term_memory != "":
                                try:
                                    dem.series.add(Series.objects.get(name=long_term_memory + i))
                                    linked_series += 1
                                    memory = ""
                                    long_term_memory = ""
                                    long_term_memory_list = []
                                except django.core.exceptions.ObjectDoesNotExist:
                                    long_term_memory = long_term_memory + i + ","
                                    long_term_memory_list.append(i)
                                    memory = i + ","

                            elif memory != "":
                                try:
                                    dem.series.add(Series.objects.get(name=memory + i))
                                    linked_series += 1
                                    memory = ""
                                    long_term_memory = ""
                                    long_term_memory_list = []
                                except django.core.exceptions.ObjectDoesNotExist:
                                    skipped_series.append(memory)
                                    long_term_memory = memory + i + ","
                                    long_term_memory_list.append(i)
                                    memory = i + ","
                            else:
                                memory = i + ","
                                long_term_memory = ""

                        except django.core.exceptions.MultipleObjectsReturned:
                            self.stdout.write(f"The Series {i} returned duplicate elements")
                            if long_term_memory != "":
                                try:
                                    dem.series.add(Series.objects.get(name=long_term_memory + i))
                                    linked_series += 1
                                    memory = ""
                                    long_term_memory = ""
                                    long_term_memory_list = []
                                except django.core.exceptions.ObjectDoesNotExist:
                                    self.stdout.write(f"LT:The Series {long_term_memory + i!r} does not exist")
                                    skipped_series.append(long_term_memory)
                                    long_term_memory = long_term_memory + i + ","
                                    long_term_memory_list.append(i)
                                    memory = i + ","

                        else:
                            if debug:
                                self.stdout.write(f"Entry {i} linked")

                    if debug:
                        self.stdout.write("Linking Videos")
                    for i in videos:
                        try:
                            dem.videos.add(Video.objects.get(id=i))
                            linked_videos += 1

                        except django.core.exceptions.ObjectDoesNotExist:
                            skipped_videos.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            self.stdout.write(f"The Video {i} returned duplicate elements")

                        else:
                            if debug:
                                self.stdout.write(f"Entry {i} linked")
            self.stdout.write(f"Successfully linked {linked_series} series")
            self.stdout.write(f"Successfully linked {linked_videos} videos")
            self.stdout.write(f"Successfully linked {linked_topics} topics")
            self.stdout.write(f"Skipped {len(skipped_videos)} videos")
            self.stdout.write(f"Skipped {len(skipped_series)} series")
            self.stdout.write(f"Skipped {len(skipped_topics)} topics")
