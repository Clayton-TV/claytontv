import csv
from django.core.management.base import BaseCommand, CommandError
from catalogue.management.commands.ImportAll import Command as Import
from catalogue.management.commands.LinkAll import Command as Link


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser): #This adds a debug coption to the command
        parser.add_argument(
            "--DEBUG", # This is the option.
            action="store_true", ## In this case it stores that the whether this option has been called or not, if it has it will return true when queried.
            help="Runs the command with Debug on", # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        print("Starting Import")
        Import.myimport(self,options["DEBUG"])
        print("Starting Linking")
        Link.mylink(self,options["DEBUG"])

    def CleanID(self, ItemIn):
        ItemOut = ItemIn.replace(" ","")
        ItemOut = ItemOut.replace("'", "")
        ItemOut = ItemOut.replace("[", "")
        ItemOut = ItemOut.replace("]", "")
        ItemOut = ItemOut.replace("-", "")
        ItemOut = ItemOut.replace("—", "")
        return ItemOut
