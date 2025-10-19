from django.core.management.base import BaseCommand

from catalogue.management.commands.link_demographics import Command as Demographics
from catalogue.management.commands.link_ministry import Command as Ministry
from catalogue.management.commands.link_series import Command as Series
from catalogue.management.commands.link_videos import Command as Video


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.mylink(options["DEBUG"])

    def mylink(self, debug):
        self.stdout.write("Linking Demographics")
        Demographics().link_demographics("CSV/Demographics.csv", debug)
        self.stdout.write("Linking Ministries")
        Ministry().link_ministries("CSV/Ministry.csv", debug)
        self.stdout.write("Linking Videos")
        Video().link_videos("CSV/Videos.csv", debug)
        self.stdout.write("Linking Series")
        Series().link_series("CSV/Series.csv", debug)

    def old_clean_id(self, item_in):
        item_out = item_in.replace(" ", "")
        item_out = item_out.replace("'", "")
        item_out = item_out.replace("[", "")
        item_out = item_out.replace("]", "")
        item_out = item_out.replace("-", "")
        item_out = item_out.replace("—", "")
        return item_out

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
