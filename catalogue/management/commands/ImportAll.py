import csv
from django.core.management.base import BaseCommand, CommandError
from catalogue.management.commands.ImportTopics import Command as Topics
from catalogue.management.commands.ImportBibleBooks import Command as Bible
from catalogue.management.commands.ImportDemographics import Command as Demographics
from catalogue.management.commands.ImportMinistries import Command as Ministries

class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser): #This adds a debug coption to the command
        parser.add_argument(
            "--DEBUG", # This is the option.
            action="store_true", ## In this case it stores that the whether this option has been called or not, if it has it will return true when queried.
            help="Runs the command with Debug on", # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        Bible.imp_bible(self,"CSV/Bible Books.csv",options["DEBUG"])
        Demographics.imp_demographics(self,"CSV/Demographics.csv", options["DEBUG"])
        Ministries.imp_ministries(self,"CSV/Ministry.csv", options["DEBUG"])
        Topics.imp_topics(self,"CSV/Topics.csv", options["DEBUG"])

