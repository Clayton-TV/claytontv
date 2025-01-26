import csv
from django.core.management.base import BaseCommand, CommandError
from catalogue.management.commands.ImportTopics import Command as Topics
from catalogue.management.commands.ImportBibleBooks import Command as Bible
from catalogue.management.commands.ImportDemographics import Command as Demographics
from catalogue.management.commands.ImportMinistries import Command as Ministries
from catalogue.management.commands.ImportSpeakers import Command as Speakers
from catalogue.management.commands.ImportVideos import Command as Videos
from catalogue.management.commands.ImportSeries import Command as Series



class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser): #This adds a debug coption to the command
        parser.add_argument(
            "--DEBUG", # This is the option.
            action="store_true", ## In this case it stores that the whether this option has been called or not, if it has it will return true when queried.
            help="Runs the command with Debug on", # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.myimport(options["DEBUG"])

    def myimport(self,Options):
        #the order here is important, some of the imports might have link functionality
        print("Import Bible Books")
        Bible.imp_bible(self,"CSV/Bible Books.csv",Options)
        print("Import Demographics")
        Demographics.imp_demographics(self,"CSV/Demographics.csv", Options)
        print("Import Ministries")
        Ministries.imp_ministries(self,"CSV/Ministry.csv", Options)
        print("Import Topics")
        Topics.imp_topics(self,"CSV/Topics.csv", Options)
        print("Import Speakers")
        Speakers.imp_speakers(self, "CSV/Speakers.csv", Options)
        print("Import Videos")
        Videos.imp_videos(self, "CSV/Videos.csv", Options)
        print("Import Series")
        Series.imp_series(self, "CSV/SSeries.csv", Options)
