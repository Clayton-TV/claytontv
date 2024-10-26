import csv
from django.core.management.base import BaseCommand, CommandError

from catalogue.management.commands.LinkDemographics import Command as Demographics


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
        Demographics.link_demographics(self,"CSV/Demographics.csv", Options)


