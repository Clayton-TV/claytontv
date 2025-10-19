from django.core.management.base import BaseCommand

from catalogue.management.commands.import_bible_books import Command as Bible
from catalogue.management.commands.import_demographics import Command as Demographics
from catalogue.management.commands.import_ministries import Command as Ministries
from catalogue.management.commands.import_series import Command as Series
from catalogue.management.commands.import_speakers import Command as Speakers
from catalogue.management.commands.import_topics import Command as Topics
from catalogue.management.commands.import_videos import Command as Videos


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.myimport(options["DEBUG"])

    def myimport(self, debug):
        # the order here is important, some of the imports might have link functionality
        self.stdout.write("Importing Bible Books")
        Bible().imp_bible("CSV/Bible Books.csv", debug)
        self.stdout.write("Importing Demographics")
        Demographics().imp_demographics("CSV/Demographics.csv", debug)
        self.stdout.write("Importing Ministries")
        Ministries().imp_ministries("CSV/Ministry.csv", debug)
        self.stdout.write("Importing Topics")
        Topics().imp_topics("CSV/Topics.csv", debug)
        self.stdout.write("Importing Speakers")
        Speakers().imp_speakers("CSV/Speakers.csv", debug)
        self.stdout.write("Import Videos")
        Videos().imp_videos("CSV/Videos.csv", debug)
        self.stdout.write("Import Series")
        Series().imp_series("CSV/Series.csv", debug)
