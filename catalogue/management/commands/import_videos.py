import csv
import re
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand

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
        self.imp_videos("CSV/Videos.csv", options["DEBUG"])

    def parse_video_date(self, date_string, video_id, alt_string):
        # self.stdout.write(date_string)
        # self.stdout.write(alt_string)
        # self.stdout.write(video_id)
        try:
            date_out = datetime.strptime(date_string, "%d/%m/%Y")
        except ValueError:
            if self.id_has_date(video_id):
                date_out = datetime.strptime(self.get_id_date(video_id), "%d/%m/%Y")
            else:
                date_out = datetime.strptime(alt_string, "%Y-%m-%d")
        return date_out

    def id_has_date(self, video_id):
        return any(
            video_id[i] == "." and i + 3 < len(video_id) and video_id[i + 3] == "." for i in range(0, len(video_id))
        )

    def get_id_date(self, video_id):
        for i in range(0, len(video_id)):
            if video_id[i] == ".":
                break

        day = video_id[i - 2 : i]
        day = re.sub(r"[A-Za-z]", "0", day)
        if int(day) > 31:
            day = "0" + day[1]
        month = video_id[i + 1 : i + 3]
        year = video_id[i + 4 : i + 6]
        if int(year) < 2008:
            year = "08"
        date = day + "/" + month + "/" + "20" + year
        date = re.sub(r"[A-Za-z]", "0", date)
        # self.stdout.write(date)
        return date

    def imp_videos(self, filepath, debug):
        skipped_ids = []
        if debug:
            self.stdout.write("The command ran and:")  # Debug Text
        Video.objects.all().delete()
        with Path(filepath).open(encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:  # cycles through the row of the dictionary previously created.
                if debug:  # Debug Text
                    self.stdout.write(str(row))  # Debug Text
                    self.stdout.write(f"Imported {row['Name']}")  # Debug Text
                if row["URL"] == "":
                    if debug:
                        self.stdout.write(f"Skipped {row['Name']} as no URL")
                    skipped_ids.append(row["ID"])
                else:
                    try:
                        Video.objects.create(
                            id=row["ID"],
                            id_number=row["ID Number"],
                            # bible_book=row['bible_book'],
                            description=row["Description"],
                            url=row["URL"],
                            # ministry = row['ministry'],
                            # number_in_series = row['number_in_series'],
                            name=row["Name"],
                            # speaker = row['speaker'],
                            # is_livestream = row['IsLivestream'],
                            # topic = row['topic']
                            thumbnail=row["Thumbnail"],
                            date_recorded=self.parse_video_date(
                                row["DateRecorded"], row["ID Number"], row["DateCreated"]
                            ),
                            date_created=datetime.utcnow().strftime("%Y-%m-%d"),
                            date_modified=datetime.utcnow().strftime("%Y-%m-%d"),
                            # labels = somelabel this will probably be created at the same time
                            # channel = row["Channel"],
                            # series = row[series],
                        )
                    except Exception as e:
                        if debug:
                            self.stdout.write(f"Error importing {row['Name']}: {e}")
                        skipped_ids.append(row["ID"])
        self.stdout.write("The following IDs were skipped due to issues:")
        self.stdout.write(str(skipped_ids))
