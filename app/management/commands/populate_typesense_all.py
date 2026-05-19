from django.core.management.base import BaseCommand

from app.management.commands.populate_typesense_bible_books import Command as Bible
from app.management.commands.populate_typesense_channels import Command as Channels
from app.management.commands.populate_typesense_demographics import Command as Demographics
from app.management.commands.populate_typesense_ministries import Command as Ministries
from app.management.commands.populate_typesense_series import Command as Series
from app.management.commands.populate_typesense_speakers import Command as Speakers
from app.management.commands.populate_typesense_topics import Command as Topics
from app.management.commands.populate_typesense_videos import Command as Videos

# Standing on the shoulders of giants...


class Command(BaseCommand):
    help = "Send database content to Typesense to index"

    def add_arguments(self, parser):  # This adds a debug option to the command
        parser.add_argument(
            "--DEBUG",  # This is the option.
            action="store_true",
            help="Runs the command with Debug on",  # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.myimport(options["DEBUG"])

    def myimport(self, debug):
        self.stdout.write("Populating Typesense with Bible Books")
        Bible().populate_bible_books(debug)
        self.stdout.write("Populating Typesense with Channels")
        Channels().populate_channels(debug)
        self.stdout.write("Populating Typesense with Demographics")
        Demographics().populate_demographics(debug)
        self.stdout.write("Populating Typesense with Ministries")
        Ministries().populate_ministries(debug)
        self.stdout.write("Populating Typesense with Series")
        Series().populate_series(debug)
        self.stdout.write("Populating Typesense with Speakers")
        Speakers().populate_speakers(debug)
        self.stdout.write("Populating Typesense with Topics")
        Topics().populate_topics(debug)
        self.stdout.write("Populating Typesense with Videos")
        Videos().populate_videos(debug)
