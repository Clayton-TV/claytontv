# ruff: noqa: C901
import csv
from pathlib import Path

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
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.link_ministries("CSV/Ministry.csv", options["DEBUG"])

    def clean_id(self, item_in):
        symbols_to_strip = " '[]-—"
        item_out = item_in.strip(symbols_to_strip)
        return item_out

    def link_ministries(self, filepath, debug):
        if debug:
            self.stdout.write("The command ran and:")  # Debug Text
        with Path(filepath).open(encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            skipped_videos = []
            skipped_series = []
            linked_series = 0
            for row in reader:  # cycles through the row of the dictionary previously created.
                if debug:  # Debug Text
                    self.stdout.write(str(row))  # Debug Text
                    self.stdout.write(f"Linked {row['Name']}")  # Debug Text

                videos = self.clean_id(row["Video_ids"]).split(",")
                series = self.clean_id(row["Series"]).split(",")

                try:
                    min_obj = Ministry.objects.get(name=row["Name"])

                except django.core.exceptions.ObjectDoesNotExist:
                    self.stdout.write(f"The entry {row['Name']} does not exist")

                except django.core.exceptions.MultipleObjectsReturned:
                    self.stdout.write(f"The entry {row['Name']} returned duplicate elements")

                else:
                    min_obj.videos.clear()

                    for i in videos:
                        try:
                            min_obj.videos.add(Video.objects.get(id=i))

                        except django.core.exceptions.ObjectDoesNotExist:
                            skipped_videos.append(i)

                        except django.core.exceptions.MultipleObjectsReturned:
                            self.stdout.write(f"The Video {i} returned duplicate elements")
                # Series linking:
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
                        min_obj.series.add(Series.objects.get(name=i))
                        linked_series += 1
                        memory = ""
                        long_term_memory = ""
                        long_term_memory_list = []

                    except django.core.exceptions.ObjectDoesNotExist:
                        if long_term_memory != "":
                            try:
                                min_obj.series.add(Series.objects.get(name=long_term_memory + i))
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
                                min_obj.series.add(Series.objects.get(name=memory + i))
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
                                min_obj.series.add(Series.objects.get(name=long_term_memory + i))
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
            self.stdout.write("The following video IDs were skipped as they do not exist:")
            self.stdout.write(str(set(skipped_videos)))
            self.stdout.write(f"Total of {len(set(skipped_videos))} skipped videos")
            self.stdout.write("The following series were skipped as they do not exist:")
            self.stdout.write(str(set(skipped_series)))
            self.stdout.write(f"Total of {len(set(skipped_series))} skipped series")
            self.stdout.write(f"A total of {linked_series} series were linked")
