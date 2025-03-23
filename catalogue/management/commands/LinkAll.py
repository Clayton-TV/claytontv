import csv
from django.core.management.base import BaseCommand, CommandError

from catalogue.management.commands.LinkDemographics import Command as Demographics
from catalogue.management.commands.LinkMinistry import Command as Ministry
from catalogue.management.commands.LinkVideos import Command as Video
from catalogue.management.commands.LinkSeries import Command as Series


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug coption to the command
        parser.add_argument(
            "--DEBUG", # This is the option.
            action="store_true",  # In this case it stores that the whether this option has been called or not, if it has it will return true when queried.
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.mylink(options["DEBUG"])

    def mylink(self,Options):
        print("Linking Demographics")
        Demographics.link_demographics(self,"CSV/Demographics.csv", Options)
        print("Linking Ministries")
        Ministry.link_ministries(self, "CSV/Ministry.csv", Options)
        print("Linking Videos")
        Video.link_videos(self, "CSV/Videos.csv", Options)
        print("Linking Series")
        Series.link_series(self, "CSV/Series.csv", Options)


    def CleanID(self, ItemIn):
        ItemOut = ItemIn.replace(" ","")
        ItemOut = ItemOut.replace("'", "")
        ItemOut = ItemOut.replace("[", "")
        ItemOut = ItemOut.replace("]", "")
        return ItemOut