# ruff: noqa: T201,T203,F401,F403,F405,F821,E501,E203,W292,W391,N801,N802,N803,N804,N805,N806,N807,N813,N814,F821,N999,PTH123,C901

from django.core.management.base import BaseCommand

from catalogue.management.commands.ImportDemographics import Command as Demographics
from catalogue.management.commands.ImportMinistries import Command as Ministries
from catalogue.management.commands.ImportSeries import Command as Series
from catalogue.management.commands.ImportSpeakers import Command as Speakers
from catalogue.management.commands.ImportTopics import Command as Topics
from catalogue.management.commands.ImportVideos import Command as Videos
from catalogue.management.commands.import_bible_books import Command as Bible


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser):  # This adds a debug coption to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",  ## In this case it stores that the whether this option has been called or not, if it has it will return true when queried.
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.myimport(options["DEBUG"])

    def myimport(self, Options):
        # the order here is important, some of the imports might have link functionality
        print("Importing Bible Books")
        Bible().imp_bible("CSV/Bible Books.csv", Options)
        print("Importing Demographics")
        Demographics().imp_demographics("CSV/Demographics.csv", Options)
        print("Importing Ministries")
        Ministries().imp_ministries("CSV/Ministry.csv", Options)
        print("Importing Topics")
        Topics().imp_topics("CSV/Topics.csv", Options)
        print("Importing Speakers")
        Speakers().imp_speakers("CSV/Speakers.csv", Options)
        print("Import Videos")
        Videos().imp_videos("CSV/Videos.csv", Options)
        print("Import Series")
        Series().imp_series("CSV/Series.csv", Options)
