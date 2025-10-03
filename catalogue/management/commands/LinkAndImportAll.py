# ruff: noqa: T201,T203,F401,F403,F405,F821,E501,E203,W292,W391,N801,N802,N803,N804,N805,N806,N807,N813,N814,F821,N999,PTH123,C901

from django.core.management.base import BaseCommand

from catalogue.management.commands.ImportAll import Command as Import
from catalogue.management.commands.LinkAll import Command as Link


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug coption to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",  ## In this case it stores that the whether this option has been called or not, if it has it will return true when queried.
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        print("Starting Import")
        Import().myimport(options["DEBUG"])
        print("Starting Linking")
        Link().mylink(options["DEBUG"])

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
