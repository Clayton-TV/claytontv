# ruff: noqa: T201,T203,F401,F403,F405,F821,E501,E203,W292,W391,N801,N802,N803,N804,N805,N806,N807,N813,N814

from django.core.management.base import BaseCommand

from catalogue.management.commands.LinkDemographics import Command as Demographics
from catalogue.management.commands.LinkMinistry import Command as Ministry
from catalogue.management.commands.LinkSeries import Command as Series
from catalogue.management.commands.LinkVideos import Command as Video


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug coption to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",  # In this case it stores that the whether this option has been called or not, if it has it will return true when queried.
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.mylink(options["DEBUG"])

    def mylink(self, Options):
        print("Linking Demographics")
        Demographics().link_demographics("CSV/Demographics.csv", Options)
        print("Linking Ministries")
        Ministry().link_ministries("CSV/Ministry.csv", Options)
        print("Linking Videos")
        Video().link_videos("CSV/Videos.csv", Options)
        print("Linking Series")
        Series().link_series("CSV/Series.csv", Options)

    def OldCleanID(self, ItemIn):
        ItemOut = ItemIn.replace(" ", "")
        ItemOut = ItemOut.replace("'", "")
        ItemOut = ItemOut.replace("[", "")
        ItemOut = ItemOut.replace("]", "")
        ItemOut = ItemOut.replace("-", "")
        ItemOut = ItemOut.replace("—", "")
        return ItemOut

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
